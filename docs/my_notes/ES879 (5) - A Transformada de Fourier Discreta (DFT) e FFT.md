# Módulo 1: O Que é a Transformada de Fourier Discreta (DFT)?

Nas aulas passadas, vimos que a Transformada de Fourier de um sinal digital gera um espectro contínuo na frequência ($\omega$). O problema? Computadores possuem memória finita; eles não conseguem processar uma variável contínua infinita. A **Transformada de Fourier Discreta (DFT)** resolve isso "fatiando" (amostrando) também o eixo das frequências. Nós pegamos o espectro contínuo e escolhemos calcular a energia apenas em $N$ "pontos" ou fatias específicas de frequência.

## 1.1. As Equações Fundamentais da DFT

Seja um sinal físico $x[n]$ que você gravou no laboratório. Ele tem uma duração finita, possuindo um tamanho de **$L$ amostras**. Para calcular a DFT, nós escolhemos um número matemático de fatias de frequência chamado **$N$**, onde obrigatoriamente $N \ge L$.

As frequências amostradas serão espaçadas uniformemente por $\omega_k = \frac{2\pi k}{N}$.

- **A Transformada Direta (Do Tempo para Frequência):**
    
    $$X[k] = \sum_{n=0}^{N-1} x[n]e^{-j2\pi kn/N}$$
    
    _O que isso faz?_ Pega as suas amostras de tempo $x[n]$, multiplica por fatias complexas giratórias, e cospe os "pesos" ou as energias em cada caixa de frequência $k$.
    
- **A Transformada Inversa - IDFT (Da Frequência para o Tempo):**
    
    $$x[n] = \frac{1}{N} \sum_{k=0}^{N-1} X[k]e^{j2\pi kn/N}$$
    
    _O que isso faz?_ Reconstrói o seu sinal original somando os senos e cossenos com os pesos que o computador calculou.
    

## 1.2. Resolução Espectral e o Truque do "Zero Padding"

A **Resolução Espectral ($\Delta f$)** diz o quão "fino" ou detalhado é o seu pente de frequências. Se você tem picos muito próximos, precisa de uma resolução alta para enxergar os dois sem que se misturem. A fórmula da resolução em Hertz é:

$$\Delta f = \frac{1}{NT}$$

Onde $T$ é o período de amostragem do seu sensor físico (o inverso da taxa de amostragem, $T = 1/F_s$).

**O que acontece se eu quiser um gráfico de frequência mais definido, mas minha gravação de áudio ($L$) foi muito curta?** Aí entra uma das técnicas mais vitais em processamento de sinais: o **Zero Padding (Preenchimento com Zeros)**. Você gravou apenas $L=10$ amostras, mas avisa ao MATLAB que quer calcular uma DFT de $N=100$ pontos. O computador automaticamente pegará os seus $10$ dados reais e vai colar $90$ zeros no final do arquivo antes de aplicar a fórmula.

- _Isso cria informação nova?_ Não. O sinal não ganha frequências mágicas.
    
- _O que isso faz fisicamente?_ Isso "interpola" o seu gráfico no domínio da frequência. Os pontos calculados ficam mais próximos um do outro ($\Delta f$ diminui pois o $N$ no denominador aumentou), deixando as curvas do gráfico contínuas, bonitas e fáceis de ler os topos dos picos.
    

> **Estudo de Caso do Zero Padding (Exemplo 1 da Aula):** O professor pegou a onda $y(t) = \sin(4\pi t)$, que possui uma frequência pura de $f = 2$ Hz.
> 
> - _Cenário A ($L=10, N=10, T=0,1$s):_ Sem zero padding. A resolução é $\Delta f = 1$ Hz. O gráfico fica terrível, um triângulo reto feio no lugar do pico.
>     ![](https://i.imgur.com/5keEHqr.png)
> - _Cenário B ($L=10, N=100, T=0,1$s):_ Com zero padding agressivo. A resolução vira $\Delta f = 0.1$ Hz. O gráfico não é mais um pico quebrado, mas uma "montanha" suave. Mas note: como o sinal original era curto ($L=10$), a montanha é "gorda", ou seja, o pico se espalha indicando uma leitura pobre.
>     ![](https://i.imgur.com/z6HROZd.png)
> - _Cenário C ($L=100, N=100, T=0,01$s):_ O sinal original é longo ($L=100$). A resolução natural é boa e o pico no gráfico fica "espetado" fininho em $2.5$ Hz.
>     ![](https://i.imgur.com/bVdTlzs.png)
> - _Cenário D ($L=100, N=10000, T=0,01$s):_ Gravação longa ($L=100$) aliada a Zero padding massivo ($N=10000$). O gráfico fica perfeito e a agulha atinge quase perfeitamente o valor verdadeiro de $1.9 \dots 2.0$ Hz.
>     ![](https://i.imgur.com/I5FIzPG.png)

## 1.3. A Simetria Circular e Outras Propriedades Matemáticas

A DFT tem propriedades diferentes da Transformada clássica porque, para o computador, calcular $N$ fatias assume que **o seu sinal de tempo é periódico e repete para o infinito** de $N$ em $N$ blocos. Isso cria o fenômeno da **Simetria Circular** ou Deslocamento Circular.

Imagine que você escreve as suas amostras ao redor de uma roleta ou de um relógio, em vez de uma linha reta.

$$[x'[n] = x[n-k]_N]$$

Atrasar um sinal digital na DFT significa girar a roleta. O elemento que sai do fim da fila ($N-1$) reaparece magicamente na posição inicial ($0$).

Outra consequência vital disso é a **Convolução Circular**. Multiplicar espectros no domínio da DFT ($X_1[k] X_2[k]$) não faz a convolução reta normal que aprendemos, mas sim uma convolução onde os sinais giram em círculo uns sobre os outros:

$$x_3[m] = \sum_{n=0}^{N-1} x_1[n] x_2[m-n]_N$$

# Módulo 2: O Processamento de Sinais Reais (Evitando Desastres)

Neste módulo, aplicamos a matemática anterior no mundo real da engenharia, criando Filtros Digitais.

## 2.1. O Filtro Linear e o Truque para não dar "Aliasing"

Se você tem um filtro LTI com uma equação interna de tamanho $M$ e o seu sinal útil tem um tamanho de gravação $L$. Você quer aplicar o filtro no sinal multiplicando as DFTs de ambos no MATLAB:

$$Y[k] = H[k] X[k]$$

Para voltar ao tempo filtrado, basta aplicar a Inversa: $y[n] = \text{IDFT}\{Y[k]\}$.

**O PERIGO MORTAL DA CONVOLUÇÃO CIRCULAR:** Se você fizer a DFT deles de tamanho curto, a convolução vai "girar" na roleta e o fim do sinal filtrado vai se atropelar com o começo do sinal, sujando seus dados irremediavelmente (fenômeno de _aliasing_ por convolução circular).

_A Regra de Ouro da Filtragem Digital:_ Para evitar que o rabo do sinal bata na própria cabeça dentro do computador, a matriz da DFT (o seu $N$) precisa ser preenchida com zeros (Zero Padding) até ser **pelo menos igual à soma dos tamanhos menos um**:

$$N \ge L + M - 1$$

## 2.2. O Fenômeno de "Vazamento Espectral" (Leakage) e o Janelamento

Quando você grava um sinal no mundo real, você não grava para o infinito. Você liga o sensor num momento e desliga em outro. Matematicamente, isso equivale a pegar a onda e multiplicá-la por um pulso quadrado bruto $w[n]$ (chamamos isso de Janela Quadrada).

$$\hat{x}[n] = w[n]x[n]$$

_Qual o problema disso?_ O corte brusco da janela quadrada introduz "quinas vivas" de $0$ para $1$ e de $1$ para $0$ no sinal. Em processamento de sinais, quinas significam harmônicas de altíssima frequência artificiais. Isso faz com que a energia daquela única frequência pura do seu sinal comece a "escorrer" ou "vazar" pelo chão do gráfico inteiro da DFT. O nome disso é **Vazamento Espectral (Leakage)**. A resolução da DFT é estragada por esse lixo fantasma nas laterais.

### A Solução: Janelas Especiais (Suavizadoras)

Para atenuar o _leakage_, os engenheiros inventaram janelas de recorte $w[n]$ que, em vez de cortarem o sinal como um machado, começam em zero, sobem suavemente, deixam o sinal central passar, e descem suavemente para zero novamente no fim do arquivo.

> **Exemplo 4 da Aula (A Guerra contra o Leakage):** O professor criou um sinal complexo misturando $10$, $20$, $35$ e $37.8$ Hz. Note que $35$ e $37.8$ estão perigosamente grudados e podem ser difíceis de diferenciar no gráfico.
> 
> - **Teste com Janela Quadrada (Corte Bruto):** No gráfico, o vazamento (as ondas que espirram pela base) é tão caótico que as bases dos picos se fundem num chiado enorme.
>     
> - **Teste com Janela de Hanning:** A janela esmaga o começo e o fim do sinal (formato de sino suave). O vazamento espectral desaparece por completo (o "chão" do gráfico fica quase totalmente zerado). Porém, o custo foi que as agulhas ficaram "gordinhas", e agora o 35 e o 37.8 quase se encostam no meio.
>     
> - **Teste com Janela Gaussiana e Tukey:** Trazem compromissos excelentes. A janela de _Tukey_ deixa o centro do sinal intocado e apenas suaviza as beiradas, gerando picos limpos sem destruir a amplitude do sinal principal no tempo.
>     

_[ESPAÇO PARA IMAGEM: Cole aqui as maravilhosas comparações visuais do Exemplo 4 (Slides 34 a 37). Observe atentamente no gráfico "Pyy" como a "sujeira" da base desaparece da Janela Quadrada para a de Hanning/Tukey]_

# Módulo 3: A Transformada Rápida de Fourier (FFT)

O nome "FFT" (Fast Fourier Transform) assusta, mas na verdade a FFT não é uma nova Transformada. A FFT é simplesmente um algoritmo computacional inventado para calcular a mesmíssima fórmula da DFT apresentada no Módulo 1, só que na velocidade da luz.

## A Matriz e o Fator "Twiddle" ($W_N$)

Os matemáticos notaram que a parcela $e^{-j2\pi/N}$ se repete incontáveis vezes calculando a somatória. Eles batizaram isso de $W_N$ (Twiddle factor):

$$W_N = e^{-j2\pi/N} \implies X[k] = \sum_{n=0}^{N-1} x[n] W_N^{kn}$$

Usando isso, o cálculo maçante pode ser escrito de uma só vez numa Matriz quadrada mágica que processa as amostras brutas ($x_N$) para dar os picos de frequência limpos ($X_N$):

$$X_N = W_N \cdot x_N$$

Para retornar da frequência e reconstruir o sinal físico, basta bater a matriz conjugada na inversa:

$$x_N = \frac{1}{N} W_N^* \cdot X_N$$

A **FFT** é um atalho que fatora essa matriz de um jeito esperto, cortando drasticamente o número de multiplicações que o processador do computador precisa fazer. É por isso que ela é a base de todo o processamento de áudio digital, MP3, 4G e Wifi no mundo atual.