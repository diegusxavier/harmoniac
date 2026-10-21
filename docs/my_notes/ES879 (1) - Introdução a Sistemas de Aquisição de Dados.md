# Sistema Metrônico

- **Objetivo:** Regular a resposta da planta/processo de forma autônoma, fazendo com que a saída seja igual à entrada desejada (setpoint).
- **Planta ou Processo:** Sistema a ser controlado. Pode compreender variáveis e parâmetros mecânicos, elétricos, magnéticos, térmicos, fluídicos, etc.
- **Saída:** Resposta do sistema.
- **Sensor:** Realiza a aquicição da saída, convertendo a variável medida em um sinal elétrico através de um sistema de aquisição de dados (*DAQ*).
- **Entrada (setpoint):** Valor a ser seguido pelo sistema; geralmente um sinal de referência elétrico.
- **Erro:** Diferença entre a saída obtida e a entrada desejada.
- **Controlador:** Corrige a resposta do sistema a partir do erro.
- **Atuador:** Aplica um estímulo sobre a planta a partir do comando do controlador, convertendo sinal elétrico em estímulo físico.

![](https://i.imgur.com/5ilDOKx.png)

# Sinais e Sistemas

- **Sinais:** São variáveis físicas que variam no tempo/espaço e transmitidas através dos estágios do sistema de medição.
- **Sistemas:** São dispositivosd que realizam operações sobre os sinais, modificando suas características espaciais/temporais ou espectrais.
- Operações como filtragem e amplificação caracterizam técnicas de **processamento de sinais**.
- O **processamento de sinais** pode ser realizado via hardware ou software, empregando algoritmos para manipular matematicamente os sinais transmitidos.
## Sistema de processamento digital de sinais

Fatores a considerar na implementação de um DSP :
- Custo computacional e consumo de memória;
- Resolução, faixa de operação e tempo de resposta;
- Qualidade e fidelidade da informação temporal e espectral.

![](https://i.imgur.com/2zSLzSB.png)

- **Conversor A/D:** Converte o sinal analógico de entrada $x(t)$ em um sinal digital de entrada $x[n]$.
- **Processador de Sinais Digitais:** Computador, microcontrolador oou circuito lógico/gate array que realiza operações sobre o sinal de entrada $x[n]$, retornnando um sinal de saída $y[n]$.
- **Conversor D/A:** Converte o sinal digital de saída $y[n]$ em um sinal analógico de saída $y(t)$.

## Classificação de Sinais 

- **Sinal escalar real:** $x(t)=Asin(\omega t)$
- **Sinal escalar complexo:** $x(t)=Ae^{j\omega t} = Acos(\omega t) + jAsin(\omega t)$
- **Sinal multi-dimensional:** $I(x, y, t)  = Ae^{j\alpha x}e^{j\beta y}e^{j\omega t}$
- **Sinal multi-canal:**$$
\mathbf{X}(t) = \begin{bmatrix}
x_1(t) \\
x_2(t) \\
x_3(t)
\end{bmatrix}
$$
- **Analógico:** Contínuo em magnitude e tempo;
- **Discreto:** Contínuo em magnitude e discretizado no tempo;
- **Digital:** Quantizado em magnitude e discretizado no tempo.

- **Sinal determinístico:** Pode ser definido explicitamente por uma expressão matemática ou tabela;
- **Sinal Aleatórrio:** Possui comportamento imprevisível, mas pode ser caracterizado através de parâmetros estatísticos.

# Conversão A/D e D/A

## Conversão A/D

Conversão de sinais analógicos dde entrada em sinais digitais que possam ser processados pelo DSP.

![](https://i.imgur.com/YdAPTEM.png)

- **Amostragem:** Adquire amostras do ainal analógico de entrada $x_a(t)$ em intervalos discretos de tempo (**intervalo de amostragem $T$**), resultando em um sinal amostrado $x[n]=x_a(t)$.
- **Quantização:** Converte a magnitude de $x_a$ em intervalos discretos (níveis) finitos, gerando um sinal quantizado $x_q[n]$.
- **Codificação:** Converte os níveis quantizados $x_q[n]$ em uma sequência binária para processamento no computador.

## Amostragem

- O **sinal amostrado** $x[n]$ é a representação discreta do sinal analógico adquirido $x_a(t)$ a um período de amostragem $T$.

![](https://i.imgur.com/uPZlu0v.png)

- A amostragem é realizada por um circuito **sample and hold (S/H)**.
- O circuito adquire amostras continuamente durante um intervalo de tempo (**sample time**).
- Subsequentemente, o circuito mantém o valor de $x[n]$ constante até que a conversão A/D seja finalizada (**hold time**).
- O tempo de conversão A/D deve ser menor do que o hold time, enquanto o período de amostragem $T$ deve ser maior que a soma do sample time e do hold time.

![](https://i.imgur.com/qHHx9aE.png)
(circuito sample and hold)
### Amostragem do sinal de acordo com a frequência

- O tempo contínuo $t$ é correlacionado às amostragens discretas $n$ pela **frequência/taxa de amostragem** $F_s=\frac{1}{T}$
$$t=nT=\frac{n}{F_s}=n\frac{2\pi}{\Omega_s}$$
- A amostragem de um sinal periódico com frequência $F$ resulta em
$$x_a(t)=Acos(2\pi Ft+\theta)$$
$$x[n]=Acos\left(2\pi F\frac{n}{F_s} + \theta \right)= Acos(2\pi fn+\theta)$$
onde $f=\frac{F}{F_s}$ é a **frequência relativa/normalizada**.

- Em termos de frequência angular, temos:
$$x_a(t)=Acos(\Omega t+ \theta)$$
$$x[n]=Acos(\Omega nT + \theta) = Acos(\omega n+\theta)$$
onde $\omega=\Omega T = 2\pi \frac{F}{F_s} = 2 \pi f$ é a **frqeuência angular normalizada**.

### Periodicidade da amostragem

- O sinal $x[n]=Acos(2\pi fn + \theta)$ é periódico a cada $N$ amostragens.
$$x[n]=x[n+N]$$
$$cos[2\pi fn] = cos[2\pi f (n+N)] = cos[2\pi fn + 2\pi fN]$$
portanto, $2\pi fN = 2\pi k$, onde $k=0, 1, 2, 3, ...$


- Seja $x[n]=Acos(2\pi fn + 2\pi k)$. Frequências no sinal discreto são distintas somente se:
$$-\frac{1}{2}\leq f \leq \frac{1}{2}$$
devido a que: $-\pi \leq 2\pi f \leq \pi$.

- Da mesma forma, para $x[n]=Acos(\omega n + 2\pi k)$:
$$-\pi \leq \omega \leq \pi$$
- Note que, para o sinal analógico, qualquer frequência $-\infty < F < \infty$ é distinta. A restrição de $|f|\leq \frac{1}{2}$ se deve ao efeito a amostragem $F_s$.

![](https://i.imgur.com/K1wGtk7.png)

- Como $f= \frac{F}{F_s}$, a **frequência máxima** que pode ser distinta pela amostragem é:
$$F_{max}=fF_s = \frac{F_s}{2}=\frac{1}{2T}$$
- Em frequência angular:
$$\Omega_{max}=\frac{2\pi F_s}{2}= \pi F_s = \frac{\pi}{T}$$
### Teorema de Nyquist (ou teorema da amostragem)

- Para que o sinal seja amostrado corretamente (mantendo a informação espectral), a frequência de amostragem deve satisfazer o critério
$$F_s\geq 2F_{max} = F_N$$
onde $F_N$ é a **frequência de Nyquist**.
- Componentes de frequência que excedem a frequência de Nyquist ($F_N = F_s/2$) são rebatidas para a banda passante como sinais espúrios (_aliases_), gerando o fenômeno de _aliasing_ e a consequente distorção irreversível da informação espectral.

#### Exemplo
- Sinal analógico: $y(t)=sin(2\pi 0,1t) + sin(2\pi t)$
- $F_1=0,1$ Hz e $F_2 = 1$ Hz $\Rightarrow F_{max} = 1$ Hz
- $F_N=2$ Hz
- Sinal amostrado: $y[n]= sin \left(2\pi \frac{0,1}{F_2}n \right) + sin \left(2\pi \frac{1}{F_s}n \right)$
![](https://i.imgur.com/NWFkhQg.png)
![](https://i.imgur.com/7GbuO8i.png)



## Quantização

- A **quantização** $x_q[n]=Q\{x[n]\}$  converte a magnitude contínua de $x(t)$ em níveis discretos, produzindo um **erro de quantização** $e_q[n] = x_q[n] - x[n]$.
- O operador $Q$ pode arredondar ou truncar o valor de $x_q[n]$.
- O incremento $\Delta$ entre níveis de quantização define a resolução do sistema. O número de níveis $L$ necessários para obter a **resolução** desejada é calculado por
$$\Delta=\frac{x_{max}-x_{min}}{L-1}$$
onde os valores máximo e minimo de $x[n]$ definem a **faixa dinâmica** do sinal.

![](https://i.imgur.com/YV1yNe3.png)

### Conversor flash (sumultâneo)
- Utiliza divisores de tensão para comparar o sinal analógico de entrada a níveis quantizados de referência.
- A conversão é realizada em **paralelo**, resultando em alta velocidade de processamento.
- São necessários $2^L-1$ comparadores para realizar a conversão em $L$ níveis.

![](https://i.imgur.com/Mlr2gpk.png)

### Conversor de rampa dupla (integrador)
- O integrador produz um sinal linearmente decrescente (rampa) modulado pela magnitude da tensão de entrada.
- O sinal de controle acumula valores até $L$ para inicializar o contador.
- Após atingir o valor final, o circuito de controle inverte a chave de entrada para uma tensão de referência, produzindo uma rampa de descarga positiva e acumulando valores no contador.
- Ao final do ciclo de descarga, os valores binários são transferidos à memória de saída.
- O tempo de subida (carregamento) é controlado pelo circuito de contagem.
- O tempo de descida é medido pelo contador.
- A conversão é mais lenta do que o conversor flash.

![](https://i.imgur.com/opEDgSo.png)
![](https://i.imgur.com/sCuvK7N.png)

![](https://i.imgur.com/gAXZpnN.png)
![](https://i.imgur.com/JageTTQ.png)
![](https://i.imgur.com/Up1sVyM.png)

### Conversor de aproximações sucessivas
- Determina a tensão digital de saída por tentativa e erro.
- A relação entre tensão e código binário é tabelada para a faixa de aplicação do sistema

![](https://i.imgur.com/3W423O2.png)

## Codificação

- A **codificação** converte os níveis quantizados em códigos binários.
- Para uma palavra de $b$ bits, são gerados $2^b$ códigos.
- Assim, para codificar $L$ níveis, o número mínimo de bits necessários é
$$b \geq log_2L$$
## Conversão D/A

- Geração de sinal analógico a partir da entrada digital.
- Circuito S/H cria buffer para evitar erros de conversão na transição de valores binários.
- Filtro passa-baixas de saída suaviza o ripple do sinal.
- É necessário preencher os *“gaps”* do sinal discreto para produzir uma saída analógica.

![](https://i.imgur.com/sX84yXH.png)

### Conversor de Escada

- Formado por uma cadeia de resistores $R, 2R, ..., 2^{N-1}R$.
- As chaves $S_1, ..., S_N$ são controladas pelos bits do sinal digital $b_1,  ...,  b_N$ ($b_1$ é o bit mais significativo).
- A corrente que entra no AMPOP é modulada pelas chaves, resultando em uma tensão de saída
$$v_0=-V_{REF} \left[ \frac{b_1}{s¹} + \frac{b_2}{2²} + ... + \frac{n_N}{2^N} \right]$$
- Note que um número maior de bits $N$ implica em resistores cada vez maiores.

![](https://i.imgur.com/N7fnhHh.png)

### Conversor R-2R

- Formado somente por resistores $R$ e $2R$.
![](https://i.imgur.com/2A0DyQv.png)

### Circuito Sample & Hold

$$\hat{x}(t) = x(nT), \quad nT \le t \le (n+1)T$$
- Note que o circuito S/H produz um atraso no sinal de saída que depende do interval de amostragem
![](https://i.imgur.com/eqvtNHQ.png)


### Segurador de Primeira Ordem

- Os intervalos amostrados são tradados como funções lineares (característica espectral aprimorada).
$$\hat{x}(t) = x(nT) + \frac{x(nT) - x(nT - T)}{T}(t - nT), \quad nT \le t \le (n + 1)T$$

![](https://i.imgur.com/62sSimg.png)

### Interpolação linear

- Utiliza a amostra atual para predizer o comportamento futuro do sinal.
$$\hat{x}(t) = x(nT - T) + \frac{x(nT) - x(nT - T)}{T}(t - nT), \quad nT \le t \le (n + 1)T$$
![](https://i.imgur.com/pESQDAE.png)


