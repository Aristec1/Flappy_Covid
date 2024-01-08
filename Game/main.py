from pygame.locals import * # Importa as funções e constantes do ".locals"
import pygame # Importa a biblioteca de jogos do python
import random # Deixará tudo aleatório
import sys  # Será usado para fechar o programa

### Variáveis Globais ###
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
CORONA = 'content/sprites/corona.png'
BACKGROUND = 'content/sprites/background.png'
VACCINE = 'content/sprites/vacina.png'

### Função para ajustar as imagens na Tela após abrir o programa ###
def welcomeScreen():
    playerx = int(SCREENWIDTH/5) # ajusta o "corona" no eixo X do plano.
    playery = int((SCREENHEIGHT - GAME_SPRITES['corona'].get_height())/2) # ajusta o "corona" no eixo Y do plano.
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2) # ajusta a "tela inicial" no eixo X do plano.
    messagey = int(SCREENHEIGHT*0.13) # ajusta a "tela inicial" no eixo Y do plano.
    basex = 0
    while True:
        for event in pygame.event.get(): # É um registrador de eventos que analiza a opção escolhida no momento.
            # Esta parte faz sair do programa quando fechar no ícone "X".
            if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # Aqui são as opções de movimentação no jogo fornecidas pelo usuário.
            elif event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_UP):
                return
            ### Se um dos controles for ou não selecionado pelo usuário, o jogo atualiza a tela para recomeçar um novo jogo ###
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))    
                SCREEN.blit(GAME_SPRITES['corona'], (playerx, playery))    
                SCREEN.blit(GAME_SPRITES['message'], (messagex,messagey ))    
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))    
                pygame.display.update()
                FPSCLOCK.tick(FPS)

### Função Principal onde contem os calculos, movimentações, ações e sons no jogo ###
def mainGame():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    # Cria 2 seringas no meio da tela
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    #lista seringas maiores
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    #lista seringas menores
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    ### Variáveis adicionais para movimentação ###
    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8 #velocidade do covid após o usuário dar o comando.
    playerFlapped = False # é verdadeiro apenas quando o covid estiver 'voando'.

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # Ela retorna True se o corona colidir.
        if crashTest:
            return     

        ### Verificador de Pontuação ###
        playerMidPos = playerx + GAME_SPRITES['corona'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['vaccine'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score +=1
                print(f"Sua pontuação é {score}") 
                GAME_SOUNDS['point'].play()

        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False            
        playerHeight = GAME_SPRITES['corona'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # Movendo as seringas para a esquerda
        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Adiciona uma nova seringa quando a primeira estiver prestes a cruzar a parte mais à esquerda da tela.
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # Remove a seringa se estiver fora da tela
        if upperPipes[0]['x'] < -GAME_SPRITES['vaccine'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        
        # Animando os Sprites
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['vaccine'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['vaccine'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['corona'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery> GROUNDY - 25  or playery<0:
        GAME_SOUNDS['hit'].play()
        return True
    
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['vaccine'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['vaccine'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['corona'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['vaccine'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False

def getRandomPipe():
# Gera duas seringas, uma na posição padrão em baixo e outra em cima rotacionada para baixo.
    pipeHeight = GAME_SPRITES['vaccine'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1}, #upper Pipe
        {'x': pipeX, 'y': y2} #lower Pipe
    ]
    return pipe

### Está função serve para iniciar o jogo ###
if __name__ == "__main__":
    pygame.init() # Faz iniciar todos os módulos da biblioteca Pygame.
    FPSCLOCK = pygame.time.Clock() # cria um objeto para ajudar a controlar o tempo.
    pygame.display.set_caption('Flappy Covid-19') # Título que aparece na aba aberta do jogo.
    
    ''' Carrega os números na inicialização '''
    GAME_SPRITES['numbers'] = ( 
        pygame.image.load('content/sprites/0.png').convert_alpha(),
        pygame.image.load('content/sprites/1.png').convert_alpha(),
        pygame.image.load('content/sprites/2.png').convert_alpha(),
        pygame.image.load('content/sprites/3.png').convert_alpha(),
        pygame.image.load('content/sprites/4.png').convert_alpha(),
        pygame.image.load('content/sprites/5.png').convert_alpha(),
        pygame.image.load('content/sprites/6.png').convert_alpha(),
        pygame.image.load('content/sprites/7.png').convert_alpha(),
        pygame.image.load('content/sprites/8.png').convert_alpha(),
        pygame.image.load('content/sprites/9.png').convert_alpha(),
    )

    ''' Carrega o plano de fundo na inicialização '''
    GAME_SPRITES['message'] =pygame.image.load('content/sprites/message.png').convert_alpha()
    
    ''' Carrega a base do jogo na inicialização '''
    GAME_SPRITES['base'] =pygame.image.load('content/sprites/base.png').convert_alpha()
    
    ''' Carrega as vacinas na inicialização '''
    GAME_SPRITES['vaccine'] =(pygame.transform.rotate(pygame.image.load(VACCINE).convert_alpha(), 180), 
    pygame.image.load(VACCINE).convert_alpha()
    )

    ''' Carrega os sons do jogo na inicialização '''
    GAME_SOUNDS['die'] = pygame.mixer.Sound('content/sounds/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('content/sounds/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('content/sounds/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('content/sounds/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('content/sounds/wing.wav')

    ''' Carrega o plano de fundo na inicialização '''
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()

    ''' Carrega o Corona virus na inicialização '''
    GAME_SPRITES['corona'] = pygame.image.load(CORONA).convert_alpha()

    ### Loop Principal ###
    while True:
        welcomeScreen() # Mostra a tela principal ao executar o código
        mainGame() # Função principal do jogo
