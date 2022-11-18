Hello, world!

# Sumário

1. [Sobre o projeto](#sobre-o-projeto)
2. [Preparando o Ambiente AWS](#preparando-o-ambiente-aws)
3. [Configurando a VPC](#configurando-a-vpc)
    - [Configuração VPC inicial](#configuração-vpc-inicial)
    - [Configurando a Sub-rede](#configurando-a-sub-rede)
    - [Configurando a entrada de internet](#configurando-a-entrada-de-internet)
    - [Configurando um endpoint para o s3 bucket](#configurando-um-endpoint-para-o-s3-bucket)
4. [Configurando o EC2](#configurando-o-ec2)
5. [Configurando o Banco de dados](#configurando-o-banco-de-dados)
    - [Configuração inicial do bd](#configuração-inicial-do-bd)
    - [Configurando o banco e a tabela](#configurando-o-banco-e-a-tabela)
6. [Configurando o S3 Bucket](#configurando-o-s3-bucket)
    - [Inserindo dados no bucket](#inserindo-dados-no-bucket)
7. [Configurando o IAM](#configurando-o-iam)
8. [Configurando o Lambda](#configurando-o-lambda)
    - [Configuração inicial lambda](#configuração-inicial-lambda)
    - [Lidando com dependências](#lidando-com-dependências)
    - [Configurando evento teste](#configurando-evento-teste)
    - [Configurando eventos](#configurando-eventos)


# Sobre o projeto

Este projeto é um desafio técnico para a entrevista técnica da empresa Edesoft.

Todas as dependências necessárias já estão no repositório.

O programa deve realizar o seguinte processo:

* Obter os dados de um arquivo csv armazenado em um _bucket s3_.
* Tratar os dados baseados nos campos necessários.
* Armazenar em um banco de dados.

__este é o código final__

# Preparando o Ambiente AWS

Antes de carregar o código para o Lambda, é necessário criar algumas configurações, que faremos no passo-a-passo:

__Pré-requisito:__ Criar/Ter uma conta AWS Amazon.

## Configurando a VPC  
---
Na AWS, para que a maioria dos serviços da aws se comuniquem é necessário configurá-los dentro de uma VPC, é uma boa prática colocar seus serviços dentro de uma VPC, pois permite maior controle sobre o fluxo de dados, as permissões e a segurança geral.

Pode-se criar mais de um aplicativo por VPC e a AWS monta um VPC padrão para sua conta, mas aqui criaremos uma do zero.

### Configuração vpc inicial
---

__Acesse o [painel VPC](https://console.aws.amazon.com/vpc/).__

__Na sessão "Your VPC", podemos criar uma VPC em "Create VPC"__

__Para este passo-a-passo o nome será 'my-vpc-01', mas você pode colocar o nome que quiser.__

Agora, vamos definir a partição de nossa rede:

mais a frente nesse tutorial, vamos criar subredes classe C como 10.0.1.x/24 ou 10.0.5.x/24, logo precisamos de uma Rede classe B.

Um pequeno sumário dos tipos de rede:

Classe A  
1-126.xxx.xxx.xxx (padrão) ou  
255.0.0.0 e /8 (máscara de rede)  

Classe B  
128-191.0-255.xxx.xxx (padrão) ou  
255.255.0.0 e /16 (máscara de rede)

Classe C  
192-223.0-255.0-255.xxx (padrão) ou  
255.255.255.0 e /24 (máscara de rede)

no caso da AWS, se utiliza máscara de rede, e portanto pode-se utilizar o ip estático que preferir, para esse tutorial usaremos o prefixo 10.0.0.0 com uma Classe B

__Portanto, no IP CIDR ficará 10.0.0.0/16__

Não utilizaremos IPv6, portanto podemos criar a VPC com essas configurações.

### Configurando a Sub-rede
---

Para este projeto, precisamos somente de uma sub-rede com acesso à internet (a internet serve apenas para vermos os resultados.)

Na sessão "Subnets" podemos criar uma subnet em "Create Subnet"

Escolha a VPC que acabamos de criar.

__Escolha um nome para a subrede, para o tutorial colocaremos de "public-1c",__

__Escolha a zona da sua subrede, para o tutorial será "us-east-1c"__

As zonas são baseadas na sua região, caso queira trocar de região, pode trocar no navegador do console.

*__!!! Lembre-se da zona escolhida, pois os serviços deverão ser montados na mesma zona, para evitar cobranças adicionais !!!__*

Como montamos uma rede classe B, podemos montar a subrede classe C como preferir.

__Para o tutorial, colocaremos o CIDR como 10.0.1.0/24__

Você pode criar mais de uma subrede de uma vez, se preferir.

__Após criar a subrede, selecione ela no painél de subredes, vá em "Actions" > "Modify auto-assign IPv4 settings" e habilite "Enable auto-assign public IPv4 Address"__, isso garantirá que os serviços da subrede tenham acesso público.

### Configurando a entrada de internet
---
Para que nossa VPC tenha acesso à internet, é necessário que esteja associada à um gateway de internet e que sua rota esteja definida.

__Na seção "Internet gateways", podemos criar uma gateway em "Create internet gateway"__

__Defina um nome para o gateway, para o tutorial colocaremos "my-internet-gateway"__

Depois de criar a gateway é necessário associar ele à vpc.

__Selecione o gateway na seção de gateways, vá em "Actions" > "Attach to VPC" e selecione o vpc.__

E depois de associado, precisamos criar a rota de acesso.

O AWS já cria um roteador padrão que você pode renomear.

__Selecione o roteador, vá em "Routes" > "Edit Routes" > "Add Route"__

__Defina o destino dessa nova rota como 0.0.0.0/0 (qualquer endereço de ip)__

__Defina o alvo como nosso gateway, escolha "Internet Gateway" e então o gateway criado.__

Pronto, agora os serviços criados na vpc conseguem se comunicar à internet.

### Configurando um endpoint para o s3 bucket
---
Mais a frente, quando associarmos a função Lambda à vpc ela não conseguirá mais obter informações do bucket, já que conseguirá se comunicar somente com serviços dentro da rede (um processo mais complicado que não passa pelo gateway adicionado ao router)[^note], portanto precisamos criar um endpoint para conseguir accesá-lo.

[^note]: Ou pelo menos essa é a impressão que ficou quando tentei utilizar o vpc padrão que a Amazon entrega, passei literalmente uma noite inteira tentando entender o porque da função Lambda não conseguir acessar o balde.

Um endpoint permite que 

Existem dois tipos de endpoints: Interface e Gateway, que funcionam para diferentes serviços da aws, para o s3 devemos utilizar o Gateway.

__Em "Endpoints", podemos criar um em "Create Endpoints"__

__Dê uma tag para seu endpoint, no tutorial nomearemos de "s3-bucket-endpoint"__

__Selecione a categoria "AWS Services"__

__Na aba dos serviços, filtre por "s3" e escolha o serviço com o formato:__  
> com.amazonaws.sua-região.s3 | amazon | Gateway

__Selecione o vpc e o roteador__

Você pode especificar a política de acesso, mas neste tutorial, deixaremos em acesso total.

## Configurando o EC2

Antes de configurarmos o banco de dados, precisamos criar um EC2 para poder acessar e configurar o banco de dados

__Acesse o painel [EC2](https://console.aws.amazon.com/vpc/)__

__Na seção "Instances", podemos criar uma instância em "Launch Instances"__

__Dê um nome para sua instância, no tutorial nomearemos de "public-1c"__

Você pode mudar o sistema operacional e o tipo de instância, mas para o tutorial deixaremos o padrão: Amazon Linux em t2.micro

Nesse tutorial, usaremos uma chave SSH para conectar ao EC2, logo:

__Em "Key pair" vamos gerar uma chave em "Create new key pair"__

__Dê um nome para a chave e escolha o tipo de criptografia__

Se você pretende utilizar PuTTy para acessar a instância, utilize a extensão .ppk, mas se você está usando PuTTy, provavelmente já sabe acessar através dele.

__Guarde essa chave, pois é com ela que você registrará sua máquina para que possa acessar a instância__

__Em "Network Settings" vá em "Edit"__

__Escolha a vpc e a subredes criadas anteriormente__

O AWS criará por padrão um grupo de segurança que permite acesso SSH de qualquer lugar.

Você pode alterar essas e outras configurações se desejar, mas para o tutorial usaremos as configurações padrão.

Após criar a instância, espere a instânciar iniciar.

__Agora para acessar a instância precisamos de:__

__\- A chave de criptografia__
__\- O usuário de acesso (Amazon utiliza ec2-user como padrão)__
__\- O endereço DNS da instância__

Você pode verificar o DNS da instância clicando no ID da instância para ver os detalhes dela, ou através da seção SSH Client ao acessar a aba "Connect".

Abra o command line (linux) ou o prompt de comando (windows) em sua máquina e digite o comando:

    ssh -i <endereço da chave de criptografia> ec2-user@<dns da instância>

Pronto, você deve ver uma resposta mais ou menos assim:

        __|  __|_  )
        _|  (     /   Amazon Linux 2 AMI
       ___|\___|___|
    https://aws.amazon.com/amazon-linux-2/
    [ec2-user@ip-10-0-1-128 ~]$

Isso significa que a instância está pronta para ser utilizada!

__Antes de terminar, digite o comando `sudo yum install mysql` para baixar a ferramenta que utilizaremos para acessar o banco__

Pode fechar o command, mas mantenha a instância online por agora.

## Configurando o Banco de dados
---
Nesse tutorial, usaremos o MariaDB como banco de dados

### Configuração inicial do bd
---

Acesse o [painel RDS](https://console.aws.amazon.com/rds/)

Na seção "Database" podemos criar o banco em "Create Database"

Escolha "Standard create"

Selecione o MariaDB

*Utilizaremos uma configuração otimizada para o plano grátis da AWS, para evitar que haja surpresas para quem estiver utilizando.*

__Em "Templates" escolha "Free tier"__, esta opção irá configurar a maior parte do necessário.

__Em "Settings" escolha o nome da instância do banco, defina o nome de usuário e a senha para a conta administradora do banco de dados.__

__Em "Storage" escolha o tipo de armazenamento ("Storage type")General Purpose SSD (gp2), defina o tamanho ("Allocated storage") para 20 GiB e desabilite escalamento automático "Store Autoscaling"__ para evitar que o banco aumenteo tamanho e passe o limite do plano gratuito.

__Em "Connectivity", em "Compute resource", escolha "Connect to EC2 Instance"__, isso vai configurar a conexão vpc do banco automaticamente para a mesma do EC2

__Ainda em "Connectivity", em "VPC security group", selecione "Choose existing" e embaixo garanta que "default" esteja selecionado, deve aparecer assim:__

     -------------
    | Default   X |
     -------------

Isso vai permitir que nossa função Lambda se conecte ao banco de dados no futuro.

O AWS irá configurar automaticamente outro grupo de segurança para permitir a conexão entre o EC2 e o banco de dados.

__Clique no Id do banco de dados na seção "Databases" para ver mais detalhes sobre o banco de dados, e lá você conseguirá obter o Endpoint do banco,__ o endpoint será usado sempre que você precisar indicar onde o banco está hospedado.

Assim que o banco de dados for criado, e isso pode levar alguns minutos, você pode conectar através da instância EC2,

__Após entrar na EC2, você pode entrar no banco de dados usando o commando:__

    mysql --host <Endpoint do banco de dados> -u <usuário> -p

O terminal pedirá a senha de acesso, e após digitá-la, deve ter essa resposta no terminal:

    Welcome to the MariaDB monitor.  Commands end with ; or \g.
    Your MariaDB connection id is 41
    Server version: 10.6.10-MariaDB-log managed by https://aws.amazon.com/rds/

    Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

    MariaDB [(none)]>

### Configurando o banco e a tabela
---
Agora que temos uma sessão conectada com o gerenciador do banco de dados, vamos criar o banco e a tabela, utilizando os comandos do arquivo .sql do repositório.

Assim, teremos um banco de dados chamado edesoft_db e uma tabela chamada cessao_fundo.

As colunas podem a serem utilizadas no banco podem ser vistas no arquivo depara.xlsx

São elas que compõem os campos descritos em form.py

Após isso, você pode usar `SHOW DATABASES`, `SHOW TABLES`, `SHOW COLUMNS FROM cessao_fundo` para ver ser tudo foi implementado corretamente.

## Configurando o S3 Bucket

Configurar o bucket S3 é bem simples:

_No [painel S3](https://console.aws.amazon.com/s3/) podemos criar o bucket em "Create Bucket"._

__Dê um nome ao bucket__. Para o tutorial, nomearemos de edesoft-data-bucket.

*O nome tem que ser globalmente único, então você não poderá criar um com o mesmo nome*

E pronto, seu balde de dados s3 foi criado, agora podemos inserir dados nele.

### Inserindo dados no bucket

__Na seção "Buckets", clique no nome do bucket que foi criado anteriormente__

Você está agora no explorador de arquivos do bucket.

__Vamos criar uma pasta em "Create Folder" e nomear de "data"__. Isto vai ser importante para definir condições ao Lambda mais tarde.

Agora, vamos entrar na pasta "data" e enviar o arquivo.exemplo.csv do repositório.

Clique na pasta "Data" e depois selecione "Upload"

Nessa nova página, você pode arrastar arquivos para serem carregados, ou clicar em "Add files" para carregar arquivos manualmente ou "Add folders" para adicionar pastas.

Carregue o arquivo arquivo_exemplo.csv e clique em "Upload"

Pronto, o arquivo foi enviado para o bucket S3.

## Configurando o IAM

Antes de criar o lambda, precisamos criar um cargo que contenha as permissões necessárias para que o lambda possa se conectar com os outros serviços.

__Acesse o [painel IAM](https://console.aws.amazon.com/iamv2)__

__Na seção "Roles" podemos criar o cargo em "Create Role"__

__Em "Entrusted entity type" escolha "AWS Services", pois estamos criando o cargo para o serviço lambda.__

__Em "Use Case" escolha Lambda__

__Clique em "Next" para seguir para a próxima página.__

Agora vamos definir as permissões do cargo, em um caso real, é importante que se habilite somente serviços que serão utilizados, mas para esse tutorial, vamos habilitar permissões totais de administrador.

__Filtre as permissões por "AdministratorAccess"__

__Selecione a permissão "AdiminstratorAccess" e continue para a próxima página.__

__Dê um nome para o cargo__, para o tutorial nomearemos de "admin"

Pronto, o cargo foi criado e pode ser implementando no lambda.

## Configurando o Lambda
---
Agora que temos todas as partes configuradas (Rede, Banco, Balde, Permissões) podemos enfim criar a função lambda que vai lidar com os dados.

### Configuração inicial lambda
---

__Vá para o [painel Lambda](https://console.aws.amazon.com/lambda/)__

__Na seção "Functions" podemos criar nossa função em "Create Functions"__

__Dê um nome para a função__

__Em "Runtime" selecione a linguagem que vai ser utilizada, no nosso caso, utilize Python 3.9__

__Em "Change default execution role" escolha "Use an existing role" e selecione no campo abaixo o cargo selecionado anteriormente.__

__Em "Advanced Settings" habilite "Enable VPC" e escolha a vpc e a subrede que criamos anteriormente.__

__Em "Security groups" habilite o grupo "default".__

Pronto, agora sua função será criada e o AWS irá abrir um console para que você possa modificar/adicionar coisas ao Lambda.

### Lidando com dependências
---
A função lambda do AWS não contém bibliotecas de terceiros, exceto bibliotecas nativas do Python,

Para que o nosso código funcione ele precisa do PyMySQL, como fazer para implementar as bibliotecas então?

Existem algumas formas de solucionar esse problema, mostrarei aqui a mais simples delas:

__Todas as depêndencias devem ser instaladas em uma pasta dentro da pasta principal do projeto, você pode fazer isso com o seguinte commando:__

    pip install --target <diretório> <pacote>

O pip então instalará o pacote na pasta especificada.

No nosso caso, as depêndencias estão em `modules/lib`

__O projeto então deve ser comprimido em um arquivo .zip com o arquivo python principal na pasta raiz__

Para o nosso tutorial, comprima o arquivo lambada_function.py e a pasta modules, a estrutura do arquivo .zip deve estar:

    arquivo_comprimido.zip
    |
    | - modules
    |       - database
    |       - files
    |       - lib
    |       - model
    | - lambda_function.py

Depois de comprimido, podemos carregar ele na função Lambda.

No console da função Lambda, clique em "Upload from" e escolha ".zip file", selecione então o arquivo compactado.

Pronto, o código e suas depêndencias foram carregadas no Lambda.

### Configurando as variáveis
--
A AWS oferece formas de criar variáveis que podem ser armazenadas em serviços como o Secret Manager, mas nesse tutorial utilizaremos variáveis manuais, portanto precisamos configurar algumas coisas antes de rodar.

__Em database/db.py, configure o host, username, password e database baseado nas configurações feitas no mariadb__

__Clique em "Deploy" para salvar as mudanças__

### Configurando evento teste

Para podermos testar nossa aplicação, precisamos configurar um evento teste para que ela possa ser executada.

__Clique em "Test"__

__Como não existe um teste ainda, só podemos criar um novo__

__Dê um nome ao seu teste__

__Em template, podemos pegar formatos já existentes dos serviços da AWS, filtre por "S3" e escolha "S3 Put"__

O AWS vai gerar então um JSON igual ao que é enviado pelos buckets, só precisamos mudar algumas informações para que o teste funcione corretamente

__Altere o nome do bucket em "Records">"s3">"bucket">"name" para o nome do balde criado anteriormente.__

__Altere o a chave do objeto em "Records">"s3">"object">"key" para o diretório do objeto que está no balde, no nosso caso é `data/arquivo_exemplo.csv`__

Antes de testarmos o código, comente a linha:

    17  Session.objects.insert_no_duplicate(file.data)

    17 # Session.objects.insert_no_duplicate(file.data)

Para que o teste não altere o banco de dados por agora.

Pronto, você já pode testar o código, a conexão com o bucket s3 e com o banco de dados através da classe Database.

### Configurando eventos

Para que esse código funcione toda vez que haja uma alteração no arquivo, precisamos criar um evento

__Clique em "+ Add Trigger" no diagrama da função (fica logo acima do console)__

__Selecione o serviço S3__

__Em "Bucket" selecione o bucket criado anteriormente__

__Em "Event type" selecione "All object create events"__

Prefix e Suffix são importantes para adicionar condições ao evento, Ao adicionar um prefix o evento só será acionado por arquivos que começarem com o prefixo, ao adicionar um Suffix, só será acionado se o arquivo terminar com o sufixo.

__Adicione "data/" à Prefix__

__Adicione ".csv" à Suffix__ 

Com as configurações acima, o evento será acionado sempre que um arquivo .csv for criado, adicionado ou alterado na pasta data.

__Habilite "Recursive invocation"__, isso é um aviso que se o Lambda tiver um código que altere o arquivo no bucket s3 ele pode entrar em um loop eterno.

Pronto, agora descomente o a linha de código que comentamos anteriormente.

O código agora deve funcionar sem problemas.

Como verificar?

\- Reinsira o arquivo_exemplo.csv no balde  
\- Abra a instância EC2 e entre no gerenciador usando o comando mysql  
\- Entre no banco de dados utilizando `USE edesoft` e `SELECT * FROM cessao_fundo`
