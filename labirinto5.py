import pygame
import sys
import random

# Inicialização do Pygame
pygame.init()

# Inicialize o mixer do Pygame
pygame.mixer.init()

# Carregar e tocar o som inicial
pygame.mixer.music.load("som.mp3")
pygame.mixer.music.play(1)  # -1 para loop infinito

# Carregar o som para a segunda fase
phase2_sound = pygame.mixer.Sound("som2.mp3")

# Configurações do jogo
DEFAULT_GRID_SIZE = 30  # Tamanho padrão da matriz (30x30)
GRID_SIZES = {
    pygame.K_1: (10, 10),
    pygame.K_2: (14, 14),
    pygame.K_3: (19, 19),
    pygame.K_4: (26, 26),
    pygame.K_5: (35, 35),
    pygame.K_6: (45, 45),
    pygame.K_7: (55, 55),
    pygame.K_8: (63, 63),
    pygame.K_9: (69, 69),
    pygame.K_0: (74, 74),  # Décima fase (74x74)
}
GRID_WIDTH, GRID_HEIGHT = GRID_SIZES[pygame.K_1]  # Tamanho inicial da grade (10x10)
CELL_SIZE = 20  # Tamanho inicial de cada célula (será recalculado)
WIDTH = DEFAULT_GRID_SIZE * 20  # Largura da tela
HEIGHT = DEFAULT_GRID_SIZE * 20  # Altura da tela
BG_COLOR = (0, 0, 0)  # Cor de fundo
WALL_COLOR = (0, 100, 255)  # Cor das paredes
POINT_COLOR = (255, 255, 255)  # Cor dos pontos

# Carregar a imagem do logo (Pac-Man)
logo_img = pygame.image.load("logo.png")

# Mapa do jogo
game_map = None

# Variáveis de jogo
time_left = 10  # Tempo inicial em segundos
current_phase = 1  # Fase inicial
previous_time_left = 0  # Tempo restante da fase anterior
message_display_time = 0  # Tempo restante para exibir a mensagem de incremento
message_increment_amount = 0  # Quantidade de tempo que foi incrementada

# Variáveis para controle de velocidade
MOVE_INTERVAL = int(200 * 0.8)  # Intervalo de movimento em milissegundos (20% mais rápido)
last_move_time = 0  # Última vez que o Pac-Man se moveu

# Função para gerar o mapa do jogo
def generate_game_map():
    global game_map
    width = GRID_WIDTH
    height = GRID_HEIGHT

    # Inicializa o mapa com paredes
    game_map = [[1 for _ in range(width)] for _ in range(height)]

    # Função auxiliar para verificar se uma posição é válida
    def is_valid(x, y):
        return 0 <= x < width and 0 <= y < height

    # Direções possíveis (cima, baixo, esquerda, direita)
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    # Função para embaralhar direções (para aleatoriedade)
    def shuffle_directions():
        random.shuffle(directions)

    # Gera o labirinto usando DFS
    def generate_maze(x, y):
        game_map[y][x] = 0
        shuffle_directions()
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if is_valid(nx, ny) and game_map[ny][nx] == 1:
                game_map[y + dy][x + dx] = 0
                generate_maze(nx, ny)

    # Inicia a geração do labirinto no centro do mapa
    start_x, start_y = width // 2, height // 2
    generate_maze(start_x, start_y)

    # Define as posições iniciais (2)
    game_map[1][1] = 2
    game_map[height - 2][width - 2] = 2

# Função para resetar o jogo
def reset_game():
    global game_map, pacman_pos, time_left, previous_time_left, message_display_time
    generate_game_map()
    pacman_pos = (1, 1)
    time_left = previous_time_left + (current_phase * 102)  # Ajuste do tempo baseado na fase
    message_display_time = 0  # Reseta o tempo de exibição da mensagem
    draw_game()

# Gera o mapa inicial
generate_game_map()

# Posição inicial do Pac-Man
pacman_pos = (1, 1)

# Inicialização da tela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f'Fase {current_phase}')  # Define o título da janela

# Função para desenhar o jogo na tela
def draw_game():
    screen.fill(BG_COLOR)
    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            cell = game_map[y][x]
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if cell == 1:
                pygame.draw.rect(screen, WALL_COLOR, rect)
            elif cell == 2:
                if (x, y) != (GRID_WIDTH - 2, GRID_HEIGHT - 2):  # Não desenha o Pac-Man no objetivo
                    screen.blit(logo_img, (rect.x, rect.y))  # Desenha o logo nas coordenadas do Pac-Man
            elif cell == 3:
                pygame.draw.circle(screen, POINT_COLOR, (rect.centerx, rect.centery), 3)

    # Desenha o objetivo no canto inferior direito
    rect = pygame.Rect((GRID_WIDTH - 2) * CELL_SIZE, (GRID_HEIGHT - 2) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    screen.blit(logo_img, (rect.x, rect.y))

    # Desenha o tempo restante na tela
    font = pygame.font.Font(None, 36)
    text = font.render(f"TIME: {time_left}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    # Desenha a mensagem de tempo incrementado, se aplicável
    if message_display_time > 0:
        message_text = f"+ {message_increment_amount} seconds"
        message_surface = font.render(message_text, True, (255, 255, 0))
        message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(message_surface, message_rect)

    pygame.display.update()

# Função para desenhar a mensagem "Game Over"
def draw_game_over():
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, 72)
    text = font.render("Game Over", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.update()

# Função para mover o Pac-Man
def move_pacman(direction):
    global pacman_pos
    new_pos = (pacman_pos[0] + direction[0], pacman_pos[1] + direction[1])
    if is_valid_move(new_pos):
        game_map[pacman_pos[1]][pacman_pos[0]] = 0  # Limpa a posição atual
        pacman_pos = new_pos
        if game_map[pacman_pos[1]][pacman_pos[0]] == 3:
            # Pac-Man come o ponto
            game_map[pacman_pos[1]][pacman_pos[0]] = 0
        game_map[pacman_pos[1]][pacman_pos[0]] = 2  # Define a nova posição do Pac-Man
        draw_game()

# Função para verificar se o movimento é válido
def is_valid_move(pos):
    x, y = pos
    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
        return game_map[y][x] != 1  # Não pode atravessar paredes
    return False

# Função para alterar o tamanho da grade
def change_grid_size(key):
    global GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, WIDTH, HEIGHT, logo_img
    GRID_WIDTH, GRID_HEIGHT = GRID_SIZES[key]
    CELL_SIZE = min(WIDTH // GRID_WIDTH, HEIGHT // GRID_HEIGHT)
    logo_img = pygame.image.load("logo.png")
    logo_img = pygame.transform.scale(logo_img, (CELL_SIZE, CELL_SIZE))
    reset_game()

# Função para iniciar a próxima fase
def next_phase():
    global time_left, current_phase, previous_time_left, message_display_time, message_increment_amount
    previous_time_left = time_left
    current_phase += 1
    increment_time = current_phase * 12
    message_increment_amount = increment_time  # Guarda a quantidade de tempo incrementada
    message_display_time = 30  # Exibe a mensagem por 3 segundos
    reset_game()
    
    if current_phase == 2:
        phase2_sound.play()  # Toca o som para a segunda fase

    pygame.display.set_caption(f'Fase {current_phase}')  # Atualiza o título da janela com o número da fase
    next_key = pygame.K_1 + min(current_phase - 1, 9)  # Garante que não exceda o número de fases disponíveis
    change_grid_size(next_key)  # Ajusta o tamanho da grade para a próxima fase

    # Atualiza a mensagem com o tempo incrementado
    increment = current_phase * 10
    message_display_time = 9  # Exibe a mensagem por 3 segundos

# Simula a pressão da tecla 1 ao iniciar o jogo
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))

# Loop principal do jogo
running = True
clock = pygame.time.Clock()
TIME_DECREMENT_EVENT = pygame.USEREVENT + 1
MESSAGE_DISPLAY_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(TIME_DECREMENT_EVENT, 1000)  # Define o evento para diminuir o tempo a cada segundo
pygame.time.set_timer(MESSAGE_DISPLAY_EVENT, 100)  # Define o evento para atualizar o tempo de exibição da mensagem

while running:
    current_time = pygame.time.get_ticks()  # Obtém o tempo atual em milissegundos

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()  # Para o som ao sair
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in GRID_SIZES:
                change_grid_size(event.key)
            elif event.key == pygame.K_n:
                next_phase()
        elif event.type == TIME_DECREMENT_EVENT:
            if time_left > 0:
                time_left -= 1
            else:
                draw_game_over()
                pygame.time.wait(2000)  # Aguarda 2 segundos para exibir "Game Over"
                pygame.quit()
                sys.exit()
        elif event.type == MESSAGE_DISPLAY_EVENT:
            if message_display_time > 0:
                message_display_time -= 1

    # Verifica as teclas pressionadas para movimentar o Pac-Man
    keys = pygame.key.get_pressed()
    move_direction = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP])

    # Move o Pac-Man a cada intervalo de tempo
    if move_direction != (0, 0) and current_time - last_move_time > MOVE_INTERVAL:
        move_pacman(move_direction)
        last_move_time = current_time

    # Verifica se o Pac-Man encontrou a imagem no canto inferior direito
    if pacman_pos == (GRID_WIDTH - 2, GRID_HEIGHT - 2):
        if current_phase < 10:  # Verifica se ainda há mais fases
            next_phase()  # Avança para a próxima fase
        else:
            # Caso o jogo tenha fases limitadas, pode ser colocado um fim de jogo ou reinício
            print("Você venceu todas as fases!")

    draw_game()
    clock.tick(30)  # Limita o jogo a 30 frames por segundo

pygame.quit()
sys.exit()
