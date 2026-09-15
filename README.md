# AutoClick

Programa Windows standalone (`.exe`, sem instalação) que clica sozinho, rápido
e infinito, em qualquer ponto da tela — funciona em qualquer PC, não só no
navegador.

## Como usar

1. Copie `dist\AutoClick.exe` pro PC que for usar (é um arquivo único, não
   precisa instalar nada).
2. Dê dois cliques no `AutoClick.exe`.
   - Se o Windows mostrar **"O Windows protegeu seu PC"** (SmartScreen),
     clique em **Mais informações** > **Executar assim mesmo**. Isso
     acontece porque o programa não é assinado digitalmente — é normal
     para programas pequenos feitos sob encomenda, não é vírus.
3. Passe o mouse sobre o ponto onde você quer que ele clique e aperte **F9**.
4. Aperte **F10** para começar a clicar. Aperte **F10** de novo pra parar.
   Esses atalhos funcionam **mesmo com outra janela em foco** — dá pra
   deixar clicando e ir usar outro programa.
   (Usamos F9/F10 e não F6/F7 de propósito: no Chrome/Edge, F6 foca a
   barra de endereço e F7 abre o popup de "Caret Browsing".)
5. Ajuste a velocidade (campo "Intervalo entre cliques" ou os botões
   Lento/Médio/Rápido/Insano) e, se quiser, desmarque "Clique infinito"
   pra definir uma quantidade.

## Importante

- O clique é **real** (o Windows manda pro app como se fosse você clicando
  de verdade) — funciona em qualquer site ou programa, mas isso também
  significa que ele **move o cursor de verdade**. Não dá pra mexer o mouse
  manualmente no exato instante em que ele está clicando. Use F10 pra
  pausar sempre que precisar do mouse de volta, e F10 de novo pra retomar.
- Antivírus/SmartScreen podem alertar porque é um `.exe` não assinado e
  porque "autoclicker" é um tipo de programa que antivírus costuma
  observar com atenção (falso positivo comum, não é malware). Se o
  Defender colocar em quarentena, adicione uma exceção pro arquivo.
- Não use isso pra burlar sistemas que proíbem automação nos termos de
  uso (compras concorridas, filas, formulários anti-bot etc.).
- Sites do tipo "teste de mouse"/CPS/chatter (ex. onlinemictest.com) muitas
  vezes filtram de propósito cliques repetidos rápido demais no mesmo
  pixel, porque é assim que eles detectam mouse com defeito (switch
  "bounce"). O programa já varia levemente a posição (±2px) e o
  intervalo a cada clique pra reduzir isso, mas em sites desse tipo pode
  ainda não contar — não é bug, é o próprio site rejeitando de propósito.
  Pra confirmar que o autoclique está funcionando, teste num botão comum
  de um site qualquer, não num testador de mouse.

## Recompilar do zero (se quiser alterar o código)

Precisa do Python 3 instalado na máquina que for compilar (não na máquina
que só vai *usar* o `.exe` final — essa não precisa de nada):

```
pip install pynput pyinstaller
python -m PyInstaller --onefile --windowed --name AutoClick autoclick.py
```

O executável final aparece em `dist\AutoClick.exe`.
