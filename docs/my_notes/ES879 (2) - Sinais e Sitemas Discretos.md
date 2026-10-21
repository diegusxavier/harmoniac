# 1. Sinais Discretos

## 1.1. O que são Sinais Discretos?

Um sinal discreto, denotado por $x[n]$, é fundamentalmente uma representação amostrada de um sinal analógico contínuo $x_a(t)$. Essa amostragem ocorre em intervalos regulares definidos por um período de amostragem $T$. Matematicamente, a relação é dada por:

$$x[n] = x_a(nT)$$

Onde o índice $n$ assume valores inteiros ($-\infty \le n \le \infty$) e representa o número específico da amostra coletada. Diferente do tempo contínuo $t$, no mundo discreto só existimos em "passos" inteiros de $n$.

![](https://i.imgur.com/AiQa8i2.png)

## 1.2. Formas de Representação

Existem quatro maneiras principais de representar a informação contida em um sinal discreto:

1. **Função Matemática:** Expresso como uma equação $x[n] = f(n)$, podendo ser contínua ou descontínua ao longo dos inteiros.
2. **Tabela:** Uma listagem direta dos valores de $n$ e seus correspondentes $x[n]$.
3. **Gráfico (Hastes/Stems):** Representação visual onde cada amostra é uma linha vertical terminando em um ponto, indicando sua amplitude.
4. **Sequência de Valores:** Uma lista entre chaves, como $x[n] = \{\dots, 0, 0, 1, 4, -2, 1, \dots\}$. Geralmente, utiliza-se uma seta ($\uparrow$) sob um dos valores para indicar a origem, ou seja, o instante de tempo $n = 0$.
    

## 1.3. Sinais Elementares

Alguns sinais servem como "blocos de montar" para a teoria de sistemas discretos.

- **Impulso Unitário ($\delta[n]$):** É o sinal mais fundamental. Existe apenas no instante zero, com amplitude 1, e é completamente nulo no restante do tempo.
    $$\delta[n] = \begin{cases} 1, & \text{se } n = 0 \\ 0, & \text{se } n \ne 0 \end{cases}$$
    ![](https://i.imgur.com/Y2XboEH.png)

- **Degrau Unitário ($u[n]$):** Representa o acionamento de uma chave. Vale zero no passado e estabiliza em 1 a partir do instante $n=0$.
    
    $$u[n] = \begin{cases} 1, & \text{se } n \ge 0 \\ 0, & \text{se } n < 0 \end{cases}$$
    ![](https://i.imgur.com/IHaog1E.png)

- **Rampa Unitária ($u_r[n]$):** Um sinal que cresce linearmente a cada passo a partir da origem.
    
    $$u_r[n] = \begin{cases} n, & \text{se } n \ge 0 \\ 0, & \text{se } n < 0 \end{cases}$$
    ![](https://i.imgur.com/U5ray5U.png)

- **Exponencial Real ($x[n] = a^n$):** Modela processos de crescimento ou decaimento. O comportamento depende da base $a$:
    
    - $0 < a < 1$: Decaimento exponencial suave para zero.
        
    - $a > 1$: Crescimento exponencial infinito.
        
    - $-1 < a < 0$: Decaimento oscilatório (alternando sinais positivos e negativos).
        
    - $a < -1$: Crescimento oscilatório instável.
    ![](https://i.imgur.com/qk9o4uh.png)

- **Exponencial Complexa:** Ocorre quando a base possui componentes reais e imaginárias, sendo expressa na forma polar $a = r e^{j\theta}$.
    
    $$x[n] = (re^{j\theta})^n = r^n e^{j\theta n}$$
    
    Expandindo pela relação de Euler, o sinal pode ser separado em partes reais e imaginárias oscilantes:
    
    $$x[n] = r^n [\cos(\theta n) + j \sin(\theta n)] = x_R[n] + jx_I[n]$$
    
    Isso também pode ser expresso através de magnitude e fase:
    
    $$x[n] = r^n \angle \theta n = \vert{}x[n]\vert{} \angle \phi[n]$$

## 1.4. Classificação de Sinais Discretos

### Sinais de Energia vs. Potência 
Para avaliar o conteúdo energético de um sinal digital, utilizamos somatórias ao longo de suas amostras.

- **Energia Total ($E$):** É a soma dos quadrados dos módulos de todas as amostras do sinal, de $-\infty$ a $\infty$.
    
    $$E = \sum_{n=-\infty}^{\infty} \vert{}x[n]\vert{}^2 = \sum_{n=-\infty}^{\infty} \vert{}x[n]x^*[n]\vert{}$$
    
    Um sinal é classificado como "**Sinal de Energia**" se esse somatório convergir para um valor finito ($0 \le E < \infty$). 
    Um sinal de enerfia infinita pode ter energia finita em um intervalo definido entre $-N$ e $N$:
    $$E_N = \sum_{n=-N}^{N} \vert{}x[n]\vert{}^2$$
    
- **Potência Média ($P$):** Expressa a taxa na qual a energia é entregue ao longo do tempo. É calculada tirando a média da energia $E_N$ quando a janela de tempo tende ao infinito.
    
    $$P = \lim_{N \to \infty} \frac{1}{2N+1} \sum_{n=-N}^{N} \vert{}x[n]\vert{}^2 = \lim_{N \to \infty} \frac{1}{2N+1} E_N$$
    
    Um sinal é classificado como "**Sinal de Potência**" se ele possuir potência média finita e diferente de zero.
    

> **Exemplo Prático 1: Energia e Potência de Sinais Elementares**
> 
> - **Impulso ($\delta[n]$):** Possui apenas uma amostra valendo 1. Sua energia é $E = 1^2 = 1$ (finita). Como a energia não cresce ao longo do tempo, dividi-la por um tempo infinito resulta em Potência $P = 0$. Logo, é um **Sinal de Energia**.
>     
> - **Degrau ($u[n]$):** Como ele vale 1 para sempre, somar $1^2$ infinitamente resulta em Energia $E \to \infty$. Contudo, se pegarmos um intervalo até $N$, temos $E_N = N+1$. Calculando a Potência: $P = \lim_{N \to \infty} \frac{N+1}{2N+1} = \frac{1}{2}$ (finita). Logo, é um **Sinal de Potência**.
>     
> - **Rampa ($u_r[n]$):** A rampa cresce infinitamente, logo sua Energia é $\infty$ e sua Potência também tende ao $\infty$. A rampa não se enquadra em nenhuma das duas classificações estritas.
>     

### Periodicidade e Simetria

- **Sinal Periódico:** Um sinal é periódico se ele se repete perfeitamente a cada intervalo $N$ amostras.    
    $$x[n+N] = x[n]$$
    
    _Todo sinal periódico contínuo no tempo é um sinal de potência finita_, cuja potência pode ser calculada integrando a energia em apenas um único período:    
    $$P = \frac{1}{N} \sum_{n=0}^{N-1} \vert{}x[n]\vert{}^2$$
    
- **Sinal Par (Simétrico):** O sinal reflete perfeitamente no eixo vertical.
    $$x[-n] = x[n]$$
    
- **Sinal Ímpar (Assimétrico):** O sinal é espelhado negativamente no eixo vertical.
    
    $$x[-n] = -x[n]$$
    
    (Nota: Um cosseno discreto, como $x[n] = A\cos(\omega_0 n)$, é par, enquanto um seno discreto é ímpar. _É importante notar que qualquer sinal arbitrário pode ser desmembrado como a soma de uma parcela puramente par e outra puramente ímpar_).

## 1.5. Operações Matemáticas com Sinais

Modificações comuns que aplicamos ao índice $n$ de um sinal:

1. **Deslocamento Temporal ($x[n-k]$):** Translada o sinal inteiro para a direita ou esquerda no tempo.
    
    - Se $k > 0$ (ex: $x[n-3]$): O sinal sofre um **atraso** de 3 amostras e se move para a direita.
        
    - Se $k < 0$ (ex: $x[n+2]$): O sinal sofre um **avanço** de 2 amostras e se move para a esquerda.
    ![](https://i.imgur.com/qbGvzxG.png)

1. **Folding ou Reflexão ($x[-n]$):** O sinal é rebatido (espelhado) em torno do eixo de tempo $n=0$. O que era futuro vira passado e vice-versa.
    ![](https://i.imgur.com/bZ4fEle.png)

2. **Scaling ou Downsampling ($x[\mu n]$):** Acelera a varredura do sinal multiplicando $n$ por um inteiro $\mu$. Na prática, isso causa uma dizimação, ou seja, o descarte de amostras intermediárias, resultando em uma mudança agressiva na taxa efetiva de amostragem.
![](https://i.imgur.com/5fQ8rhN.png)

### Exemplo 2

![](https://i.imgur.com/Qpi8IHh.png)
![](https://i.imgur.com/mcvcuMt.png)
![](https://i.imgur.com/atH2VOX.png)
![](https://i.imgur.com/fI44aCP.png)
![](https://i.imgur.com/nVzs4rJ.png)
![](https://i.imgur.com/ha6BM33.png)
![](https://i.imgur.com/EOP5hTq.png)

# 2. Sistemas Discretos

## 2.1. O que é um Sistema?

Um sistema é um operador matemático ou algoritmo físico $\mathcal{T}\{\cdot\}$ que processa um sinal de excitação de entrada ($x[n]$) e o converte em um novo sinal de resposta ou saída ($y[n]$).

$$y[n] = \mathcal{T}\{x[n]\}$$

## 2.2. Diagramas de Blocos

Sistemas são responsáveis por converter um sinal de entrada $x[n]$ e uma saída $y[n]$ atrav\es de uma operação/transformada $y[n]=\mathcal{T}\{x[n]\}$.
Sistemas complexos são representados desenhando interconexões entre operações digitais básicas:

![](https://i.imgur.com/NRa7Vy3.png)

### Exemplo 3

![](https://i.imgur.com/acX3x9I.png)
![](https://i.imgur.com/pJ24Ajk.png)


- **Somador (+):** Adiciona o valor instantâneo de dois sinais sem exigir memória: $y[n] = x_1[n] + x_2[n]$.
    ![](https://i.imgur.com/shPxCHJ.png)

- **Ganho ($\triangleright$ ou $a$):** Multiplica o sinal por uma constante escalar: $y[n] = a \cdot x[n]$.
    ![](https://i.imgur.com/pKrlLCV.png)

- **Multiplicador ($\times$):** Multiplica dois sinais em tempo real: $y[n] = x_1[n] \cdot x_2[n]$.
    ![](https://i.imgur.com/0URDpDR.png)

- **Atraso Unitário ($z^{-1}$):** Este é o **elemento de memória fundamental** da era digital. Ele "segura" a amostra por um ciclo de clock, disponibilizando a amostra anterior para ser processada agora: $y[n] = x[n-1]$.
    ![](https://i.imgur.com/SkFOver.png)

- **Avanço Unitário ($z$):** Exige prever o futuro captando $x[n+1]$. (Teórico, impossível em sistemas de tempo real).
    ![](https://i.imgur.com/1P2eKnh.png)

### Exemplo 4

![](https://i.imgur.com/wUMANOh.png)
![](https://i.imgur.com/kYbisel.png)
![](https://i.imgur.com/WzeYSH4.png)

## 2.3. Classificações Críticas de um Sistema

### Estático vs. Dinâmico (Memória)

- _Estático:_ A saída atual só depende da entrada deste exato momento. Exemplo: O cubo do sinal $y[n] = n \cdot x[n] + b \cdot x^3[n]$.

- _Dinâmico:_ A saída precisa "lembrar" do passado. Exemplo: $y[n] = x[n] + 3x[n-1]$.

### Invariante no Tempo vs. Variante

- _Invariante:_ A "regra do jogo" não muda com o passar do relógio. Se atrasarmos a entrada em $k$, a saída será idêntica, apenas atrasada de $k$ passos: $y[n-k] = \mathcal{T}\{x[n-k]\}$. Exemplo de sistema variante que falha no teste: O sistema $y[n] = n \cdot x[n]$ muda de ganho dependendo de _quando_ o sinal entra (devido ao fator multiplicador $n$ externo).

- _Variante:_ As características entrada-saída mudam em funnção de deslocamentois temporais na entrada, ou seja, $y[n-k] \neq \mathcal{T}\{x[n-k]\}$.
        
### Linear vs. Não-Linear:
    
- _Linear:_ Respeita rigorosamente o Princípio da Superposição. Uma combinação ponderada de sinais na entrada deve produzir a mesma combinação ponderada das saídas individuais na saída.
        $$\mathcal{T}\{a_1 x_1[n] + a_2 x_2[n]\} = a_1 \mathcal{T}\{x_1[n]\} + a_2 \mathcal{T}\{x_2[n]\}$$
    
    > **Sistemas LTI:** Acrônimo para _Linear and Time-Invariant_ (Lineares e Invariantes no Tempo). São a espinha dorsal da engenharia de controle e processamento de sinais, permitindo o uso de ferramentas poderosas como a Transformada Z e a Convolução.
    
### Causalidade:
    
- _Causal:_ O sistema opera com os pés na realidade; a saída do agora ($y[n]$) depende puramente do agora ($x[n]$) e do que já passou ($x[n-k]$).
        
- _Não-Causal:_ Tenta prever amostras que ainda não ocorreram ($x[n+1]$). Filtros não-causais são muito úteis em estúdios de gravação ou processamento de imagens (offline), onde o arquivo já está inteiramente gravado, mas são estritamente impossíveis de implementar em algoritmos ao vivo (tempo real).
        
### Estabilidade (Critério BIBO):
    
- _Estável:_ Garante que a saída jamais vai explodir para infinito se a entrada for finita.
        
- _BIBO (Bounded-Input, Bounded-Output):_ Se a excitação for restrita entre limites definidos, a resposta do sistema será garantidamente contida em limites controlados.
        

# 3. Análise de Sistemas LTI Discretos

## 3.1. A Construção da Convolução a partir de Impulsos

Qualquer sinal digital por mais caótico que seja, como $x[n] = \{1, 0, -1, 2\}$, pode ser decomposto em uma "fatiamento" de impulsos solitários, cada um deslocado para a sua posição e multiplicado pelo seu respectivo peso de amplitude.

$$x[n]\delta[n-k] = x[k]\delta[n-k]$$
![](https://i.imgur.com/kwkIxN9.png)

Portanto, a reconstrução exata do sinal é a somatória varrendo o tempo infinito:

$$x[n] = \sum_{k=-\infty}^{\infty} x[k]\delta[n-k]$$
![](https://i.imgur.com/3xMfYUm.png)

Seja a operação $y[k]=\mathcal{T}\{x[n]\}$. Se aplicarmos a operação do sistema $\mathcal{T}\{\cdot\}$ nessa somatória de impulsos, e lembrando que o sistema é linear e invariante, podemos passar o operador para dentro da soma. Onde o termo $\mathcal{T}\{\delta[n-k]\}$ representa exatamente a Resposta ao Impulso $h[n]$ do sistema, deslocada no tempo:

$$y[n] = \sum_{k=-\infty}^{\infty} x[k] \mathcal{T}\{\delta[n-k]\}$$

O resultado é a famosa **Equação de Convolução Discreta**, a pedra angular do processamento de sinais, que prevê a saída $y[n]$ a partir do histórico de entradas:

$$y[n] = x[n] * h[n] = \sum_{k=-\infty}^{\infty} x[k] h[n-k]$$

**Algoritmo Prático da Convolução** Para calcular $y[n]$ em um ponto específico $n=n_0$:

1. Inverta a memória do sistema (Folding): transforme $h[k]$ em $h[-k]$.
2. Desloque essa memória invertida até o tempo alvo $n_0$: obtendo $h[n_0 - k]$.
3. Multiplique ponto a ponto o vetor de entrada $x[k]$ com essa memória deslocada.
4. Some todos esses produtos para encontrar a resposta agregada naquele instante único.
5. Avance $n_0$ e repita infinitamente.

![](https://i.imgur.com/yJS7WmL.png)
![](https://i.imgur.com/cemQ16M.png)

## 3.2. Propriedades Matemáticas da Convolução

A estrela $(*)$ funciona como uma multiplicação algébrica permitindo simplificações:

- **Comutativa:** $x[n] * h[n] = h[n] * x[n]$.
    
- **Associativa:** $\{x[n] * h[n]\} * g[n] = x[n] * \{h[n] * g[n]\}$.
    
- **Distributiva:** $x[n] * \{h[n] + g[n]\} = x[n] * h[n] + x[n] * g[n]$.
    

## 3.3. Estabilidade Absoluta via Resposta ao Impulso

Para que um sistema LTI discreto possua a garantia de Estabilidade BIBO, a soma do valor absoluto de sua Resposta ao Impulso deve imperativamente convergir para um limite finito:

$$S_h = \sum_{n=-\infty}^{\infty} \vert{}h[n]\vert{} < \infty$$

Com base nisso, os sistemas são divididos em:

- **FIR (Finite Impulse Response):** O sinal de memória $h[n]$ desliga-se completamente após $M$ amostras. Eles são incondicionalmente estáveis, pois a somatória é contada dentro de um limite fechado: $y[n] = \sum_{k=0}^{M-1} h[k]x[n-k]$.
    
- **IIR (Infinite Impulse Response):** A resposta ao impulso nunca atinge o zero absoluto matematicamente (decaimento exponencial contínuo). A estabilidade precisa ser testada rigorosamente para provar a convergência: $y[n] = \sum_{k=0}^{\infty} h[k]x[n-k]$.
    

# 4. Equações a Diferenças (A Dinâmica Digital)

Enquanto a convolução analisa o ponto de vista externo ($h[n]$), as Equações a Diferenças focam em como a máquina funciona por dentro (recursão).

![](https://i.imgur.com/29Lmdip.png)

## 4.1. O Algoritmo de Recursão

Um sistema causal dinâmico sempre calcula a nova saída através de amostras velhas. Isso exige criar laços de realimentação em software (usando registradores de atraso $z^{-1}$) que realimentam o valor passado de volta na função.

A **Forma Geral** que descreve qualquer sistema de ordem $N$ é um filtro IIR padrão:

$$y[n] = -\sum_{k=1}^{N} a_k y[n-k] + \sum_{k=0}^{M} b_k x[n-k] = y_{zi}[n] + y_{zs}[n]$$

Onde a saída se bifurca naturalmente em duas parcelas:

- **Resposta Natural ($y_{zi}[n]$):** O que ocorre se você soltar o sistema e não injetar energia na entrada ($x=0$). Depende apenas do balanço interno da máquina.
    
- **Resposta Forçada ($y_{zs}[n]$):** O movimento forçado induzido ativamente pelo sinal que você injetou e pelo histórico de condições.
    

## 4.2. A Matemática da Solução

Assim como nas Equações Diferenciais, a resolução final obedece o teorema:

$$y[n] = y_h[n] + y_p[n]$$

(A Resposta Homogênea + A Resposta Particular).

**1. Solução Homogênea ($y_h$):** Zera-se a excitação externa ($x=0$). Assume-se uma forma exponencial $y_h[n] = \lambda^n$. Isso extrai o "Polinômio Característico" da máquina:

$$\lambda^{n-N} [\lambda^N + a_1\lambda^{N-1} + \dots + a_{N-1}\lambda + a_N] = 0$$

Ao resolver as raízes ($\lambda_i$) desse polinômio, montamos a forma da solução homogênea total com constantes indefinidas:

$$y_h[n] = C_1\lambda_1^n + C_2\lambda_2^n + \dots + C_N\lambda_N^n$$

**2. Solução Particular ($y_p$):** Procura-se encontrar um formato genérico que satisfaça a entrada aplicada no sistema. A tabela de "chutes" matemáticos clássicos para a entrada $x(n)$:

- Se for Constante $A \implies$ Chute $K$.
    
- Se for Exponencial $A \cdot M^n \implies$ Chute $K \cdot M^n$.
    
- Se for Polinômio $A \cdot n^M \implies$ Chute $K_0 n^M + K_1 n^{M-1} + \dots + K_M$.
    
- Se for Harmônica (Senos e Cossenos) $\implies$ Chute a combinação completa $K_1 \cos(\omega_0 n) + K_2 \sin(\omega_0 n)$.
    

_(Nota: Para encontrar o resultado real final ($y[n]$), soma-se as duas metades e aplicam-se as condições de contorno iniciais dadas pelo problema para fixar o valor exato das constantes $C_i$)_.

# 5. Teoria da Correlação

A correlação, na essência da estatística e no processamento, atua como uma busca de similaridade e padrões. Ao invés de prever dinâmicas como a convolução, a correlação analisa o quão parecido um sinal de teste é com um sinal gabarito, deslizando-os um por sobre o outro.

## 5.1 Correlação Cruzada (Cross-correlation)

Medimos o "match" entre dois sinais diferentes, $x[n]$ e $y[n]$, avaliando deslocamentos de lag representados por $l$.

$$r_{xy}(l) = \sum_{n=-\infty}^{\infty} x[n] y[n-l] = \sum_{n=-\infty}^{\infty} x[n+l] y[n]$$

$$r_{yx}(l) = \sum_{n=-\infty}^{\infty} y[n] x[n-l] = \sum_{n=-\infty}^{\infty} y[n+l] x[n]$$

**Relação crucial:** Podemos usar o mesmo motor de algoritmo da convolução para resolver a correlação, pois a correlação cruzada nada mais é que a convolução do sinal $x$ com o sinal $y$ espelhado/invertido no tempo: $r_{xy}(l) = x(l) * y(-l)$.

## 5.2 Autocorrelação (Autocorrelation)

Uma ferramenta essencial para encontrar periodicidades escondidas ou extrair sinais importantes de um ruído caótico. Compara o sinal $x[n]$ consigo mesmo atrasado.

$$r_{xx}(l) = \sum_{n=-\infty}^{\infty} x[n] x[n-l] = \sum_{n=-\infty}^{\infty} x[n+l] x[n]$$

_Uma peculiaridade notável:_ Quando o deslocamento é rigorosamente zero ($l=0$), os sinais se alinham perfeitamente consigo mesmos. Matematicamente, a fórmula degenera para a soma dos quadrados instantâneos, ou seja, o pico exato da autocorrelação representa perfeitamente a **Energia Total do Sinal ($E_x$)**.

![](https://i.imgur.com/VACYRQU.png)
