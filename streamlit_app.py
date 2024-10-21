import streamlit as st
import json
import matplotlib.pyplot as plt
import hashlib
from fpdf import FPDF
import os


def load_user_data():
    try:
        with open("user_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open("user_data.json", "w") as file:
        json.dump(data, file)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def calculate_consumption(appliance_data):
    total_consumption = 0
    appliance_consumption = {}
    for appliance in appliance_data:
        power = appliance['potencia']
        hours_per_day = appliance['horas']
        quantity = appliance['quantidade']
        daily_consumption = power * hours_per_day * quantity / 1000
        monthly_consumption = daily_consumption * 30
        appliance_name = appliance['nome']
        total_consumption += monthly_consumption
        appliance_consumption[appliance_name] = monthly_consumption
    return total_consumption, appliance_consumption


def get_current_energy_rate():
    return 0.85

def get_energy_rate_by_state(state):
    rates = {
        "Pará": 0.962,
        "Mato Grosso": 0.883,
        "Mato Grosso do Sul": 0.880,
        "Alagoas": 0.866,
        "Piauí": 0.854,
        "Rio de Janeiro": 0.840,
        "Amazonas": 0.835,
        "Acre": 0.828,
        "Bahia": 0.808,
        "Distrito Federal": 0.766,
        "Pernambuco": 0.764,
        "Tocantins": 0.756,
        "Minas Gerais": 0.751,
        "Ceará": 0.744,
        "Roraima": 0.735,
        "Maranhão": 0.719,
        "Rondônia": 0.709,
        "Goiás": 0.711,
        "Espírito Santo": 0.696,
        "Rio Grande do Sul": 0.691,
        "Rio Grande do Norte": 0.689,
        "São Paulo": 0.680,
        "Sergipe": 0.651,
        "Paraná": 0.639,
        "Paraíba": 0.602,
        "Santa Catarina": 0.593,
    }
    return rates.get(state, 0.85)


def generate_pdf_report(username, total_consumption, appliance_consumption):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Relatório de Consumo de Energia - {username}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Consumo Mensal Total: {total_consumption:.2f} kWh", ln=True)
    pdf.cell(200, 10, txt="Consumo por Aparelho:", ln=True)


    for appliance, consumption in appliance_consumption.items():
        pdf.cell(200, 10, txt=f"{appliance}: {consumption:.2f} kWh", ln=True)


    max_items_per_page = 10
    appliance_list = list(appliance_consumption.items())

    for i in range(0, len(appliance_list), max_items_per_page):
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt="Gráfico de Consumo por Aparelho", ln=True, align='C')
        pdf.ln(10)


        fig, ax = plt.subplots(figsize=(10, 6))
        current_items = appliance_list[i:i + max_items_per_page]
        names, values = zip(*current_items)

        ax.bar(names, values, color='skyblue')
        ax.set_xlabel('Aparelhos')
        ax.set_ylabel('Consumo (kWh)')
        ax.set_title('Consumo de Energia por Aparelho')
        plt.xticks(rotation=45, ha='right')

        for j, value in enumerate(values):
            ax.text(j, value + 0.05, f'{value:.2f}', ha='center', va='bottom')


        img_path = f"temp_chart_{i // max_items_per_page}.png"
        plt.savefig(img_path)
        plt.close(fig)


        pdf.image(img_path, x=10, w=180)

    file_path = f"{username}_relatorio.pdf"
    pdf.output(file_path)
    return file_path



def get_energy_saving_tips(consumption):
    if consumption > 500:
        return [
            "Seu consumo está alto! Considere usar aparelhos mais eficientes.",
            "Desligue aparelhos que não estão sendo usados para economizar mais."
        ]
    elif 200 <= consumption <= 500:
        return [
            "Você está no caminho certo! Verifique se há aparelhos que podem ser otimizados.",
            "Considere instalar painéis solares para reduzir ainda mais sua conta de luz."
        ]
    else:
        return [
            "Seu consumo está em um bom nível. Continue economizando!",
            "Aproveite para compartilhar suas práticas de economia com amigos e familiares."
        ]


def update_consumption_history(username, monthly_consumption):
    if "historico" not in user_data[username]:
        user_data[username]["historico"] = []
    user_data[username]["historico"].append({
        "mes": len(user_data[username]["historico"]) + 1,
        "consumo": monthly_consumption
    })
    save_user_data(user_data)


user_data = load_user_data()


st.title("EcoEnergy: Lugar certo para economizar sua energia!")
menu = st.sidebar.selectbox("Menu", ["Login", "Registrar", "TUTORIAL", "Calculadora Energética", "Lista de KWh", "Paineis Solares", "Dicas Sustentáveis"])


if menu == "Registrar":
    st.subheader("Crie uma nova conta")
    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Registrar"):
        if username in user_data:
            st.warning("Usuário já existe.")
        else:
            user_data[username] = {"password": hash_password(password), "aparelhos": []}
            save_user_data(user_data)
            st.success("Conta criada com sucesso. Vá para o login.")


elif menu == "Login":
    st.subheader("Acesse sua conta")
    username = st.text_input("Nome de usuário", key="login_user")
    password = st.text_input("Senha", type="password", key="login_pass")
    if st.button("Login"):
        if username in user_data and user_data[username]["password"] == hash_password(password):
            st.success("Login realizado com sucesso! Agora você tem acesso às demais abas.")
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.warning("Credenciais incorretas.")



if st.session_state.get("logged_in"):
    st.subheader(f"Bem-vindo, {st.session_state.username}")


    appliance_options = {
        "Eletrodomésticos": ["Geladeira/Freezer", "Fogão Elétrico", "Micro-ondas", "Máquina de lavar roupas", "Máquina de secar roupas", "Máquina de lavar louça", "Ferro de passar roupa", "Aparelho de Ar-condicionado", "Ventilador", "Aquecedor Elétrico", "Chuveiro Elétrico", "Purificador de água elétrico", "Desumidificador", "Umidificador"],
        "Entretenimento e Eletrônicos": ["Televisão", "Computador (Desktop/Notebook)", "Vídeo Game/Consoles", "Home theater", "Caixa de som", "Roteador de Internet", "Receptor de TV a cabo",
                    "Carregador de celular e tablet"],
        "Iluminação e Pequenos Aparelhos": ["Lâmpada Incandescente (Comum)", "Lâmpada Fluorescente", "Lâmpada LED", "Abajur", "Luminária", "Aspirador de Pó", "Liquidificador", "Batedeira", "Processador de Alimentos", "Cafeteira elétrica", "Chaleira elétrica", "Torradeira", "Sanduicheira/Grill Elétrico", "Forno elétrico"],
        "Outros Equipamentos": ["Secador de cabelo", "Máquina de barbear elétrica", "Escova de dentes elétrica", "Cortador de grama elétrico", "Furadeira Elétrica", "Portão Automático", "Sistema de alarme e segurança (Câmeras, sensores)", "Bombas de água para piscina ou poço"]
    }

    # Área da calculadora
    if menu == "Calculadora Energética":
        st.header("Consumo de Aparelhos")


        tabs = st.tabs(["Eletrodomésticos", "Entretenimento e Eletrônicos", "Iluminação e Pequenos Aparelhos", "Outros Equipamentos"])

        if st.session_state.get("logged_in"):

            #seleção de estado
            state = st.selectbox("Escolha seu estado", [
                "Pará", "Mato Grosso", "Mato Grosso do Sul", "Alagoas", "Piauí",
                "Rio de Janeiro", "Amazonas", "Acre", "Bahia", "Distrito Federal",
                "Pernambuco", "Tocantins", "Minas Gerais", "Ceará", "Roraima",
                "Maranhão", "Rondônia", "Goiás", "Espírito Santo", "Rio Grande do Sul",
                "Rio Grande do Norte", "São Paulo", "Sergipe", "Paraná", "Paraíba", "Santa Catarina"
            ])

        #adicionar aparelhos em diferentes áreas
        def add_appliance(area):
            with st.form(key=area):
                appliance_name = st.selectbox(f"Escolha um aparelho em {area}", appliance_options[area])
                power = st.number_input("Potência (W) do aparelho", min_value=0)
                hours = st.number_input("Horas de uso por dia do aparelho", min_value=0.0, max_value=24.0)
                quantity = st.number_input("Quantidade de aparelhos", min_value=1, value=1)
                if st.form_submit_button(f"Adicionar {area}"):
                    user_data[st.session_state.username]["aparelhos"].append({
                        "nome": appliance_name,
                        "potencia": power,
                        "horas": hours,
                        "quantidade": quantity,
                        "area": area
                    })
                    save_user_data(user_data)
                    st.success(f"Aparelho '{appliance_name}' adicionado em {area}!")


        for area in ["Eletrodomésticos", "Entretenimento e Eletrônicos", "Iluminação e Pequenos Aparelhos", "Outros Equipamentos"]:
            with tabs[["Eletrodomésticos", "Entretenimento e Eletrônicos", "Iluminação e Pequenos Aparelhos", "Outros Equipamentos"].index(area)]:
                add_appliance(area)



        st.subheader("Consumo Estimado")
        total_consumption, appliance_consumption = calculate_consumption(
            user_data[st.session_state.username]["aparelhos"])
        energy_rate = get_energy_rate_by_state(state)
        st.write(f"Consumo mensal estimado: {total_consumption:.2f} kWh")
        st.write(f"Valor estimado da conta de luz: R$ {total_consumption * energy_rate:.2f}")

        graph_type = st.selectbox("Escolha o tipo de gráfico", ["Barras", "Pizza"])

        if graph_type == "Pizza":
            st.subheader("Consumo por Aparelho (PIZZA)")
            if appliance_consumption:

                fig, ax = plt.subplots(figsize=(8, 8))
                wedges, texts, autotexts = ax.pie(
                    appliance_consumption.values(),
                    labels=appliance_consumption.keys(),
                    autopct='%1.1f%%',
                    startangle=90,
                    textprops=dict(color="w")
                )
                ax.axis('equal')  
                ax.set_title("Consumo de Energia por Aparelho")
        
                ax.legend(
                    wedges, appliance_consumption.keys(),
                    title="Aparelhos",
                    loc="center left",
                    bbox_to_anchor=(1, 0, 0.5, 1)
                )
            
                st.pyplot(fig)

        else:
            st.subheader("Consumo por Aparelho (BARRAS)")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(appliance_consumption.keys(), appliance_consumption.values(), color='skyblue')
            ax.set_xlabel('Aparelhos')
            ax.set_ylabel('Consumo (kWh)')
            ax.set_title('Consumo de Energia por Aparelho')
            plt.xticks(rotation=45, ha='right')
            for i, (name, value) in enumerate(appliance_consumption.items()):
                ax.text(i, value + 0.05, f'{value:.2f}', ha='center', va='bottom')
            st.pyplot(fig)



     
        if st.button("Atualizar Histórico de Consumo"):
            update_consumption_history(st.session_state.username, total_consumption)
            st.success("Histórico atualizado com sucesso!")

        if len(user_data[st.session_state.username].get("historico", [])) > 0:
            history = user_data[st.session_state.username]["historico"]
            months = [entry["mes"] for entry in history]
            consumption_values = [entry["consumo"] for entry in history]

            st.subheader("Histórico de Consumo")
            fig, ax = plt.subplots()
            ax.plot(months, consumption_values, marker='o')
            ax.set_xlabel("Mês")
            ax.set_ylabel("Consumo (kWh)")
            ax.set_title("Consumo Mensal ao Longo do Tempo")
            st.pyplot(fig)

   
        st.subheader("Dicas de Economia Personalizadas")
        tips = get_energy_saving_tips(total_consumption)
        for tip in tips:
            st.write(f"- {tip}")

        if st.button("Baixar Relatório em PDF"):
            file_path = generate_pdf_report(st.session_state.username, total_consumption, appliance_consumption)
            with open(file_path, "rb") as file:
                st.download_button("Clique para baixar o PDF", data=file, file_name=f"{st.session_state.username}_relatorio.pdf")

        if st.button("Resetar Dados"):
            user_data[st.session_state.username]["aparelhos"] = []  
            save_user_data(user_data)  
            st.success("Dados resetados com sucesso!")  

    elif menu == "Paineis Solares":
        st.header("Instalação de Painéis Solares")
        panels = st.number_input("Número de painéis solares", min_value=0, value=0)
        daily_production = st.number_input("Produção diária de cada painel (kWh)", min_value=0.0, value=0.0)
        installation_cost = st.number_input("Custo de instalação (R$)", min_value=0.0, value=0.0)

        if panels > 0 and daily_production > 0:
            monthly_production = daily_production * panels * 30  
            savings = monthly_production * 0.70  
            months_to_recoup = installation_cost / savings if savings > 0 else float('inf')

            st.subheader("Resultados da Instalação de Painéis Solares")
            st.write(f"Produção mensal dos painéis: {monthly_production:.2f} kWh")
            st.write(f"Economia mensal com os painéis solares: R$ {savings:.2f}")
            st.write(f"Tempo para recuperar o investimento: {months_to_recoup:.1f} meses" if months_to_recoup != float('inf') else "A economia é zero. Revise os parâmetros.")

        st.write("Informe a quantidade de painéis e a produção diária para calcular a economia.")

    elif menu == "TUTORIAL":
        st.header("Tutorial Básico de Como Utilizar o Programa")

     
        como_usar = {
            "Calculadora Energética": [
                "A calculadora é bem simples! Basta colocar os objetos que utilizam eletricidade, seu consumo médio em watts (veja a lista caso não saiba), o tempo que tal objeto é utilizado e quantos deles você tem em sua casa."
            ],
            "Lista de KWh": [
                "Na seção 'Lista de KWh', você encontrará a potência média de diversos aparelhos elétricos. Isso ajuda a estimar o consumo e a calcular a conta de luz."
            ],
            "Paineis Solares": [
                "Aqui você pode calcular a produção de energia dos painéis solares que deseja instalar. Informe o número de painéis, a produção diária de cada um e o custo da instalação."
            ],
            "Dicas Sustentáveis": [
                "Essa seção fornece dicas para economizar energia e tornar sua casa mais sustentável. Leia as dicas, com foco nos aparelhos que você mais gasta energia de acordo com a calculadora, e aplique-as no seu dia a dia!"
            ],
            "Histórico de Consumo": [
                "Acompanhe seu consumo mensal de energia ao longo do tempo. Isso ajuda a identificar padrões e a tomar decisões informadas sobre o uso de energia."
            ],
        }

     
        for categoria, instrucoes in como_usar.items():
            with st.expander(categoria):
                for instrucao in instrucoes:
                    st.write(f"- {instrucao}")

    elif menu == "Dicas Sustentáveis":
        st.header("Dicas Sustentáveis para Reduzir o Consumo de Energia")

       
        dicas = {
            "Aquecedor de água (chuveiro elétrico)": [
                "Limite o tempo de banho a 10-15 minutos para economizar energia.",
                "Considere instalar um aquecedor solar para reduzir o uso do chuveiro elétrico."
            ],
            "Ar-condicionado": [
                "Mantenha o termostato entre 23°C e 25°C para uma temperatura confortável e econômica.",
                "Use ventiladores para ajudar a circular o ar e reduzir o uso do ar-condicionado."
            ],
            "Aparelho de aquecimento elétrico": [
                "Use cobertores e roupas quentes para reduzir a necessidade de aquecimento elétrico.",
                "Considere alternativas como aquecedores a gás ou aquecedores solares."
            ],
            "Máquina de lavar roupas": [
                "Use a máquina com carga cheia para maximizar a eficiência.",
                "Escolha ciclos de lavagem com água fria sempre que possível."
            ],
            "Secadora de roupas": [
                "Seque as roupas ao ar livre sempre que possível.",
                "Limpe o filtro da secadora regularmente para otimizar o desempenho."
            ],
            "Ferro de passar roupa": [
                "Passe várias roupas de uma vez, quando o ferro já estiver quente.",
                "Utilize o modo vapor apenas quando necessário."
            ],
            "Geladeira": [
                "Verifique se as borrachas de vedação estão em bom estado para evitar perda de frio.",
                "Mantenha a temperatura entre 3°C e 5°C para economia de energia."
            ],
            "Forno elétrico": [
                "Evite abrir a porta do forno durante o cozimento para manter a temperatura.",
                "Considere usar o forno de micro-ondas para pratos menores, que consome menos energia."
            ],
            "Televisão": [
                "Desligue a TV quando não estiver em uso, em vez de deixá-la em modo de espera.",
                "Considere uma TV de LED, que consome menos energia do que modelos mais antigos."
            ],
            "Computador": [
                "Desligue o computador quando não estiver em uso, ou use o modo de hibernação.",
                "Use configurações de economia de energia para reduzir o consumo quando inativo."
            ],
            "Lâmpadas": [
                "Substitua lâmpadas incandescentes por LED, que consomem menos energia e duram mais.",
                "Aproveite a luz natural sempre que possível, abrindo cortinas e persianas."
            ],
        }

        
        for aparelho, dicas_aparelho in dicas.items():
            with st.expander(aparelho):
                for dica in dicas_aparelho:
                    st.write(f"- {dica}")



    elif menu == "Lista de KWh":

       
        st.title("Potência Média de Aparelhos Elétricos")

   
        potencia_aparelhos = {
            "Eletrodomésticos": {
                "Geladeira/Freezer": 150,
                "Fogão elétrico": 2000,
                "Micro-ondas": 1200,
                "Máquina de lavar roupas": 500,
                "Secadora de roupas": 1500,
                "Máquina de lavar louça": 1300,
                "Ferro de passar roupa": 1000,
                "Aparelho de ar-condicionado": 1200,
                "Ventiladores": 60,
                "Aquecedor elétrico": 1500,
                "Aquecedor de água (chuveiro elétrico)": 5500,
                "Purificador de água elétrico": 100,
                "Desumidificador": 300,
                "Umidificador": 40
            },
            "Entretenimento e Eletrônicos": {
                "Televisão": 100,
                "Computadores (desktop, notebook)": 200,
                "Vídeo game/consoles de jogos": 150,
                "Home theater": 200,
                "Caixas de som": 50,
                "Roteador de internet": 10,
                "Receptores de TV a cabo": 20,
                "Carregadores de celular e tablets": 5
            },
            "Iluminação e Pequenos Aparelhos": {
                "Lâmpada Incandescente (Comum)": 60,
                "Lâmpada Fluorescente": 15,
                "Lâmpada LED": 10,
                "Abajures": 15,
                "Luminárias": 20,
                "Aspirador de pó": 600,
                "Liquidificador": 350,
                "Batedeira": 200,
                "Processador de alimentos": 400,
                "Cafeteira elétrica": 800,
                "Chaleira elétrica": 1500,
                "Torradeira": 800,
                "Sanduicheira/Grill elétrico": 700,
                "Forno elétrico": 1500
            },
            "Outros Equipamentos": {
                "Máquina de secar cabelo": 1200,
                "Máquina de barbear elétrica": 10,
                "Escova de dentes elétrica": 5,
                "Cortador de grama elétrico": 1000,
                "Furadeira elétrica": 600,
                "Portão automático": 100,
                "Sistema de alarme e segurança (câmeras, sensores)": 10,
                "Bombas de água para piscina ou poço": 750
               
            }
        }

      
        for categoria, aparelhos in potencia_aparelhos.items():
            with st.expander(categoria):
                for aparelho, potencia in aparelhos.items():
                    st.write(f"{aparelho}: {potencia} W")

      
        st.info(
            "Os valores de potência são aproximados e podem variar conforme o modelo e a utilização de cada aparelho.")

st.image('C:/Users/T-Gamer/Downloads/thekings.jpg')
