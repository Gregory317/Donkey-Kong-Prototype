import pygame
import sys

# --- CONFIGURACIÓN GENERAL ---
ANCHO = 800
ALTO = 600
FPS = 60

# Colores (Estilo Retro)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (200, 50, 50)      # Mario / Jumpman
AZUL = (50, 50, 200)      # Plataformas
MARRON = (139, 69, 19)    # Barriles
CYAN = (0, 255, 255)      # Escaleras
VERDE = (50, 200, 50)     # Meta (Pauline)

# Físicas
GRAVEDAD = 0.8
FUERZA_SALTO = -13
VELOCIDAD_JUGADOR = 5
VELOCIDAD_BARRIL = 3

class Entidad(pygame.sprite.Sprite):
    """Clase base para cualquier objeto del juego"""
    def __init__(self, x, y, ancho, alto, color):
        super().__init__()
        # Aquí es donde cargarías la imagen: self.image = pygame.image.load('assets/img.png')
        # Por ahora usamos un rectángulo de color:
        self.image = pygame.Surface([ancho, alto])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Jugador(Entidad):
    def __init__(self):
        super().__init__(50, ALTO - 70, 30, 40, ROJO) # Posición inicial
        self.vel_x = 0
        self.vel_y = 0
        self.en_suelo = False
        self.en_escalera = False

    def update(self, plataformas, escaleras):
        # 1. Movimiento Horizontal
        self.vel_x = 0
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -VELOCIDAD_JUGADOR
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = VELOCIDAD_JUGADOR

        # Aplicar movimiento X
        self.rect.x += self.vel_x

        # Colisión Horizontal con plataformas (paredes)
        lista_colisiones = pygame.sprite.spritecollide(self, plataformas, False)
        for bloque in lista_colisiones:
            if self.vel_x > 0:
                self.rect.right = bloque.rect.left
            elif self.vel_x < 0:
                self.rect.left = bloque.rect.right

        # 2. Lógica de Escaleras
        # Verificamos si tocamos una escalera
        colision_escalera = pygame.sprite.spritecollide(self, escaleras, False)
        
        if colision_escalera:
            self.en_escalera = True
            if teclas[pygame.K_UP] or teclas[pygame.K_w]:
                self.vel_y = -3
            elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                self.vel_y = 3
            else:
                self.vel_y = 0 # Si no presiona nada en la escalera, se queda quieto
        else:
            self.en_escalera = False
            # 3. Gravedad (Solo si no está en escalera)
            self.vel_y += GRAVEDAD

        # Aplicar movimiento Y
        self.rect.y += self.vel_y

        # Colisión Vertical (Suelo/Techo)
        # Solo verificamos suelo si NO estamos subiendo activamente una escalera
        if not self.en_escalera: 
            lista_colisiones = pygame.sprite.spritecollide(self, plataformas, False)
            for bloque in lista_colisiones:
                if self.vel_y > 0:
                    self.rect.bottom = bloque.rect.top
                    self.vel_y = 0
                    self.en_suelo = True
                elif self.vel_y < 0:
                    self.rect.top = bloque.rect.bottom
                    self.vel_y = 0

        # Limites de pantalla
        if self.rect.bottom > ALTO: # Muerte por caída al vacío (opcional)
            self.reiniciar()
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > ANCHO: self.rect.right = ANCHO

    def saltar(self):
        # Solo saltar si está en el suelo y no en una escalera
        if self.en_suelo and not self.en_escalera:
            self.vel_y = FUERZA_SALTO
            self.en_suelo = False

    def reiniciar(self):
        self.rect.x = 50
        self.rect.y = ALTO - 70

class Barril(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y, 25, 25, MARRON)
        self.vel_x = VELOCIDAD_BARRIL

    def update(self, plataformas):
        self.rect.x += self.vel_x
        
        # Gravedad del barril (para que caiga si se acaba el piso)
        self.rect.y += 4 
        
        # Colisión con piso
        lista_colisiones = pygame.sprite.spritecollide(self, plataformas, False)
        if lista_colisiones:
            for bloque in lista_colisiones:
                self.rect.bottom = bloque.rect.top
        else:
            # Si no toca piso, cae (lógica simple para este prototipo)
            pass

        # Rebotar en los bordes de la pantalla
        if self.rect.right > ANCHO or self.rect.left < 0:
            self.vel_x *= -1
            self.rect.y += 20 # Bajar un poco al rebotar (simula bajar de nivel)

# --- CLASE PRINCIPAL DEL JUEGO ---
class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Donkey Kong Clone - Prototipo")
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.SysFont("Arial", 24)
        
        self.inicializar_nivel()

    def inicializar_nivel(self):
        # Grupos de sprites
        self.todos_los_sprites = pygame.sprite.Group()
        self.plataformas = pygame.sprite.Group()
        self.escaleras = pygame.sprite.Group()
        self.barriles = pygame.sprite.Group()

        # Crear Jugador
        self.jugador = Jugador()
        self.todos_los_sprites.add(self.jugador)

        # Crear Meta (Pauline)
        self.meta = Entidad(50, 40, 40, 40, VERDE)
        self.todos_los_sprites.add(self.meta)

        # --- DISEÑO DEL NIVEL (Coordenadas X, Y, Ancho, Alto) ---
        lista_plataformas = [
            (0, ALTO - 20, ANCHO, 20),           # Suelo base
            (0, 450, 600, 20),                   # Piso 1
            (200, 320, 600, 20),                 # Piso 2
            (0, 190, 600, 20),                   # Piso 3
            (200, 80, 200, 20),                  # Piso Meta
        ]

        lista_escaleras = [
            (400, 450, 30, 130), # Sube del suelo al piso 1
            (250, 320, 30, 130), # Sube del piso 1 al 2
            (500, 190, 30, 130), # Sube del piso 2 al 3
            (300, 80, 30, 110),  # Sube a la meta
        ]

        for plat in lista_plataformas:
            bloque = Entidad(*plat, AZUL)
            self.plataformas.add(bloque)
            self.todos_los_sprites.add(bloque)

        for esc in lista_escaleras:
            ladder = Entidad(*esc, CYAN)
            self.escaleras.add(ladder)
            self.todos_los_sprites.add(ladder)

        # Timer para generar barriles
        self.ultimo_barril = pygame.time.get_ticks()

    def generar_barril(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_barril > 3000: # Cada 3 segundos
            barril = Barril(10, 150) # Aparece arriba
            self.barriles.add(barril)
            self.todos_los_sprites.add(barril)
            self.ultimo_barril = ahora

    def ejecutar(self):
        jugando = True
        while jugando:
            # 1. Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    jugando = False
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        self.jugador.saltar()

            # 2. Actualizar Lógica
            self.jugador.update(self.plataformas, self.escaleras)
            self.barriles.update(self.plataformas)
            self.generar_barril()

            # --- DETECCIÓN DE COLISIONES JUEGO ---
            
            # Perder: Chocar con barril
            if pygame.sprite.spritecollide(self.jugador, self.barriles, False):
                print("¡Has perdido! Reiniciando...")
                self.inicializar_nivel() # Reinicio simple

            # Ganar: Tocar la meta
            if pygame.sprite.collide_rect(self.jugador, self.meta):
                print("¡Has ganado! Nivel completado.")
                self.inicializar_nivel()

            # 3. Dibujar
            self.pantalla.fill(NEGRO)
            self.todos_los_sprites.draw(self.pantalla)
            
            # Texto simple
            texto = self.fuente.render("Flechas: Mover | Espacio: Saltar", True, BLANCO)
            self.pantalla.blit(texto, (10, 10))

            pygame.display.flip()
            self.reloj.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()