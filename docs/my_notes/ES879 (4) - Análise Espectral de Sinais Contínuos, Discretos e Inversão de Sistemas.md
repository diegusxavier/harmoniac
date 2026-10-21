# 1. Análise Espectral de Sinais Contínuos

A análise em frequência permite entender como a energia de um sinal no tempo ($t$) está distribuída entre diferentes componentes de oscilação.

## 1.1. Série de Fourier (Sinais Periódicos)

Se um sinal contínuo $x(t)$ for estritamente periódico, ou seja, se repete perfeitamente a cada intervalo de tempo $T_p$ ($x(t) = x(t + T_p)$), ele pode ser construído (ou decomposto) por uma soma infinita de senos e cossenos oscilando em múltiplos inteiros de uma frequência fundamental $F_0 = 1/T_p$.

Essa decomposição matemática é a **Série Trigonométrica de Fourier**:

$$x(t) = a_0 + \sum_{k=1}^{\infty} [a_k \cos(2\pi k F_0 t) - b_k \sin(2\pi k F_0 t)]$$

- **$a_0$ (Offset DC ou Nível Médio):** É o valor médio da onda. $a_0 = \frac{1}{T_p} \int_0^{T_p} x(t)dt$.
    
- **$a_k$ (Coeficientes do Cosseno):** $a_k = \frac{2}{T_p} \int_0^{T_p} x(t) \cos(2\pi k F_0 t)dt$.
    
- **$b_k$ (Coeficientes do Seno):** $b_k = \frac{2}{T_p} \int_0^{T_p} x(t) \sin(2\pi k F_0 t)dt$.

![](https://i.imgur.com/dAXWnUY.png)

> **Dicas Vitais de Simetria:**
> 
> - Se o sinal for **par** ($x(-t) = x(t)$), a onda pode ser montada apenas com cossenos. Todos os termos **$b_k = 0$**.
>     
> - Se o sinal for **ímpar** ($x(-t) = -x(t)$), a onda pode ser montada apenas com senos. Todos os termos **$a_k = 0$**. _(Nota: Uma onda dente-de-serra padrão, como no Exemplo 1 da aula, é um sinal ímpar, logo possui apenas termos de seno)_.
>     

_![](https://i.imgur.com/eyzJbtU.png)
![](https://i.imgur.com/DxoOwyd.png)
![](https://i.imgur.com/HcT2G2O.png)

## 1.2. Densidade Espectral de Potência (Sinais Periódicos)

Sinais periódicos se estendem ao infinito, logo a sua _energia_ total é infinita, mas a sua **potência** é finita. A potência média do sinal original é calculada pela integral do quadrado do sinal no tempo. A poderosa **Relação de Parseval** garante que a potência calculada no tempo é rigorosamente igual à soma das potências de cada componente harmônica individual $c_k$ no domínio da frequência:

$$P_x = \frac{1}{T_p} \int_0^{T_p} \vert{}x(t)\vert{}^2 dt = \sum_{k=-\infty}^{\infty} \vert{}c_k\vert{}^2$$

Plotar o gráfico de $\vert{}c_k\vert{}^2$ no eixo Y contra a frequência ($kF_0$) no eixo X gera o "Espectro de Potência" (Power Density Spectrum), que mostra quais harmônicas estão roubando mais energia do sistema.

## 1.3. A Transformada de Fourier (Sinais Aperiódicos)

O que acontece se o sinal não se repetir (ex: um único pulso quadrado ou uma exponencial decrescente)? A matemática contorna isso imaginando que o sinal se repete, mas o período $T_p$ demora uma eternidade (tende ao infinito). A somatória discreta da Série se condensa e vira uma integral contínua que cobre todas as frequências da natureza. Essa é a **Transformada de Fourier** $\mathcal{F}$:

$$X(F) = \int_{-\infty}^{\infty} x(t)e^{-j 2\pi F t} dt \quad \text{ou em rad/s} \quad X(\Omega) = \int_{-\infty}^{\infty} x(t)e^{-j \Omega t} dt$$

- **No tempo:** O sinal era real $x(t)$.
    
- **Na frequência:** A Transformada $X(F)$ gera números complexos (um espectro de magnitude $\vert{}X(F)\vert{}$ e um espectro de fase $\angle X(F)$).
    
    - _Exemplo:_ O espectro de um Impulso Unitário ($\delta(t)$) resulta numa linha reta em $\vert{}X(\omega)\vert{} = 1$. Isso significa que um impacto seco carrega uma quantidade igual de energia em **todas as frequências imagináveis** do universo, simultaneamente.
        

## 1.4. Densidade Espectral de Energia (Sinais Aperiódicos)

Para sinais finitos (aperiódicos), nós usamos o conceito de Energia. A Relação de Parseval também funciona aqui, com a Densidade Espectral de Energia ($S_{xx}$) sendo a magnitude ao quadrado da Transformada contínua:

$$E_x = \int_{-\infty}^{\infty} \vert{}x(t)\vert{}^2 dt = \int_{-\infty}^{\infty} \vert{}X(F)\vert{}^2 dF$$

$$S_{xx} = \vert{}X(F)\vert{}^2 = X(F)X^*(F)$$

# 2. Análise Espectral de Sinais Discretos

Com a digitalização do mundo, não analisamos mais $x(t)$, mas sim amostras $x[n]$. A teoria de Fourier foi adaptada para arrays numéricos.

## 2.1. Série de Fourier de Sinal Discreto

Se o array digital se repete a cada $N$ amostras ($x[n] = x[n+N]$), temos um sinal discreto periódico.

$$x[n] = \sum_{k=0}^{N-1} c_k e^{j 2\pi kn / N}$$

A grande diferença é que o espectro de frequências digitais é circular. Calcular os coeficientes harmônicos de $k = 0$ até $N-1$ dá o espectro completo, sendo impossível gerar harmônicas novas fora dessa janela matemática repetitiva (elas se dobram de volta - aliasing).

## 2.2. A Transformada de Fourier de Tempo Discreto (DTFT)

Para fatias numéricas aperiódicas (ex: as primeiras $L$ amostras ligadas e o resto 0), aplicamos a somatória infinita:

$$X(\omega) = \sum_{n=-\infty}^{\infty} x[n] e^{-j\omega n}$$

A característica mais crucial da Transformada Discreta é que a curva de frequência $X(\omega)$ **é sempre periódica com um período de $2\pi$** ($X(\omega) = X(\omega + 2\pi)$). Por isso, só analisamos a banda base (de $-\pi$ até $\pi$, ou de $0$ até $2\pi$).

### Propriedades Importantes no Domínio Discreto:

- **Deslocamento Temporal:** Se você atrasar o array digital, muda apenas a fase (aparece uma exponencial imaginária multiplicando): $\mathcal{F}\{x[n-k]\} = e^{-j\omega k} X(\omega)$.
    
- **Convolução:** Como sempre, no domínio da frequência ela vira uma multiplicação limpa: $\mathcal{F}\{x_1[n]*x_2[n]\} = X_1(\omega)X_2(\omega)$.
    
- **Modulação Espectral (Deslocamento):** Multiplicar o sinal no tempo por um senoide $e^{j\omega_0 n}$ transplanta o gráfico do espectro do meio da tela para a nova frequência $\omega_0$.
    

# 3. Análise Espectral de Sistemas LTI (Filtros)

O filtro nada mais é do que a Função de Transferência do sistema avaliada no domínio das frequências ($\omega$). Se você injetar uma onda (autofunção) $x[n] = A e^{j\omega n}$, a saída da máquina LTI sempre será:

$$y[n] = A H(\omega) e^{j\omega n}$$

A função complexa $H(\omega) = \mathcal{F}\{h[k]\}$ é o **autovalor** da máquina. Ela vai esmagar a amplitude e defasar o ângulo da onda que você injetou.

> **Exemplo Prático (Slide 86):** O sistema $h[n] = (0.5)^n u[n]$ é atingido por $x[n] = 10 \cdot e^{j\frac{\pi}{2}n}$. Pela fórmula de Transformada (Exemplo 9), $H(\omega) = \frac{1}{1 - 0.5e^{-j\omega}}$. O sistema sente a frequência de entrada de $\frac{\pi}{2}$ rad/s. Avaliando: $H(\pi/2) = \frac{1}{1 - 0.5e^{-j\pi/2}} = \frac{1}{1 + 0.5j}$. Multiplicando a onda original por esse filtro, sairá do outro lado $\frac{10}{1+0.5j} \cdot e^{j\frac{\pi}{2}n}$.

## 3.1. Classificação de Filtros e Alocação

Os filtros LTI "escolhem" quais componentes de Fourier sobrevivem e quais morrem na saída.

1. **Passa-baixa (Lowpass):** Passa apenas o miolo do gráfico perto de $\omega=0$.
    
2. **Passa-alta (Highpass):** Corta o miolo perto do 0 e passa as frequências rápidas perto do limite $\omega=\pi$.
    
3. **Passa-banda (Bandpass) e Rejeita-banda (Bandstop):** Selecionam "fatias" intermediárias do espectro.
    

**Como os Engenheiros Projetam os Filtros $H[z]$:** Brincando de espalhar polos e zeros no plano $Z$:

- A "curva de ganho" desaba quando o plano de frequência passa perto de um **Zero** no círculo unitário (furos no chão).
    
- A "curva de ganho" sobe como uma montanha quando passa perto de um **Polo** (pilares esticando a lona para cima).
    
- Para criar um _Passa-baixa_, nós colocamos polos perto de $\omega=0$ (ângulo de 0 graus) para erguer o ganho ali, e enchemos de zeros perto de $\omega=\pi$ (ângulo de 180 graus no círculo unitário) para matar as altas frequências.

- Filtro passa-baixa: 
	- Polos próximo ao círculo unitário em regiões de baixa frequência (𝜔 ≈ 0) 
	- Zeros próximo no círculo unitário em regiões de alta frequência (𝜔 ≈ 𝜋). 
- Filtro passa-alta: 
	- Polos próximo ao círculo unitário em regiões de alta frequência (𝜔 ≈ 𝜋) 
	- Zeros próximo no círculo unitário em regiões de baixa frequência (𝜔 ≈ 0).

# 4. Inversão de Sistemas e Deconvolução

A **Deconvolução** é a operação reversa de engenharia. Imagine que você está gravando a voz de alguém em um teatro (sistema $T$ com ressonância e eco), e você captou o áudio distorcido $y[n]$ no microfone. Você quer remover o eco e recuperar a voz pura original $x[n]$. Para isso, você constrói digitalmente um **Sistema Inverso $T^{-1}$**.

A matemática exige que a resposta em cascata do sistema e do seu inverso se anule, restando apenas um sinal puro sem atrasos:

$$w[n] = h_I[n] * h[n] * x[n] = x[n]$$

No domínio das transformadas $Z$, isso significa que a multiplicação das duas "caixas" dá o ganho ideal absoluto de 1:

$$H[z] \cdot H_I[z] = 1$$

Logo, o filtro digital limpador de ecos ($H_I$) é apenas a Função de Transferência do teatro **de ponta-cabeça**!

$$H_I[z] = \frac{1}{H[z]} = \frac{\text{Denominador Original}}{\text{Numerador Original}}$$

### O Desafio da Estabilidade na Inversão

Ao virar a fração de cabeça para baixo, **todos os antigos Zeros do teatro viraram os novos Polos do nosso filtro de limpeza**. Como sabemos, polos fora do Círculo Unitário causam instabilidade no sistema (explodem o computador).

- **Sistemas de Fase Mínima:** São sistemas perfeitos, onde todos os polos originais E TODOS OS ZEROS originais moram de forma segura dentro do círculo unitário ($\vert{}z\vert{} < 1$). Ao inverter esses sistemas, tudo que é pólo vira zero (e vice-versa), e como todo mundo já estava do lado seguro, o filtro inverso resultante é 100% estável.
    
- Se o sistema original possuía zeros instáveis (fase mista ou não mínima), a tentativa de invertê-lo diretamente gerará pólos instáveis, arruinando a desconvolução.
    

> **Exemplo Clássico de Inversão (Slide 100):** Você leu com seus sensores a entrada $x[n] = \{1, -0.7, 0.1, 0\}$ e mediu a saída final da planta em $y[n] = \{1, 0.7, 0, 0\}$. Qual é o código de transferência que está regendo a máquina lá dentro? Aplicando a Transformada $Z$:
> 
> - $X[z] = 1 - 0.7z^{-1} + 0.1z^{-2}$
>     
> - $Y[z] = 1 + 0.7z^{-1}$
>     
> 
> Montando $H[z] = Y[z] / X[z]$ e multiplicando tudo por $z^2/z^2$ para limpar as potências negativas:
> 
> $$H[z] = \frac{z(z + 0.7)}{z^2 - 0.7z + 0.1} = \frac{z(z + 0.7)}{(z - 0.5)(z - 0.2)}$$
> 
> Os polos do sistema oculto estão localizados em $0.5$ e $0.2$, provando que a planta misteriosa é LTI e estável.