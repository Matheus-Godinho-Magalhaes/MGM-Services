import csv
import re


from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, request, render_template, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import apology, login_required, real

# Configuração aplicação Flask

app = Flask(__name__)

# Custom filter
app.jinja_env.filters["real"] = real


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configurando a library cs50 para o banco de dados SQLite
db = SQL("sqlite:///dados.db")

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/search", methods=["GET", "POST"])
def providers():
    providers = []
    print(session)
    # Captura os parâmetros de busca
    if request.method == "POST":
        service_type = request.form.get("service_type")
        location = request.form.get("location")

        #DEPOIS EU VOLTO AQUI E ADICIONO UM ORDER BY RATINGS

        # Consulta para buscar prestadores de acordo com os filtros
        query = """
                SELECT users.id, users.username, services.service_type,
                services.location, services.price,
                COALESCE(AVG(reviews.rating), 'Novo') as average
                FROM users
                JOIN services ON users.id = services.user_id
                LEFT JOIN reviews ON services.user_id = reviews.provider_id
                WHERE users.role = 'Prestador de Serviço'
            """

        params = []

        if service_type:
            query += " AND services.service_type LIKE ?"
            params.append(f"%{service_type}%")
        if location:
            query += " AND services.location LIKE ?"
            params.append(f"%{location}%")

        # Agrupando por user_id para garantir que todos os prestadores correspondentes sejam incluídos
        query += " GROUP BY users.id, services.service_type, services.location, services.price"

        # Executa a consulta apenas se houver pelo menos um filtro aplicado
        if params:
            providers = db.execute(query, *params)

    return render_template("index.html", providers=providers)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        options = ["Cliente", "Prestador de Serviço"]
        return render_template("register.html", options=options)
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        role = request.form.get("role")

        # Conferindo o formato do e-mail fornecido do lado do servidor
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if not username or not password or not confirmation or not email or not role:
            flash("Preencha todos os campos")
            return redirect("/register")
        elif password != confirmation:
            flash("As senhas fornecidas não conferem!")
            return redirect("/register")
        elif not re.match(email_regex, email):
            flash("Formato de e-mail inválido!")
            return redirect("/register")


        email_existed = db.execute("SELECT email FROM users WHERE email = ?", email)
        # o execute() retorna uma lista, e listas vazias são avaliadas como False.
        if email_existed:
            flash("Já existe um usuário com o e-mail fornecido!")
            return redirect("/register")

        #Inserindo o novo usuário no banco de dados
        hash_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", username, email, hash_password, role)

        flash("Conta criada com Sucesso")
        #Após fazer o log in eu redireciono o usuário
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        if not email:
            flash("Preencha o email!")
            return redirect("/login")
        elif not password:
            flash("Preencha a senha")
            return redirect("/login")

        #Pegando informações od meu banco de dados
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)

        #Conferindo email e senha
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return apology("usuário ou senha inválidos!", 403)

        # Iniciando a sessão
        session["user_id"] = rows[0]["id"]
        session["role"] = rows[0]["role"]

        #Redirecionando para a página inicial
        return redirect("/search")


@app.route("/logout")
def logout():
    # Limpando dados da sessão
    print(session)
    session.clear()
    print(session)
    flash("Log out realizado com sucesso")
    # Redirecionando para página inicial
    return redirect("/")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    if user[0]["role"] != "Prestador de Serviço":
        return apology("Essa função é apenas para Prestadores de Serviço!")

    service = db.execute("SELECT * FROM services WHERE user_id = ?", session["user_id"])


    if request.method == "GET":
        return render_template("profile.html", user=user[0], service=service[0] if service else None)
    else:
        service_type = request.form.get("service_type")
        price = float(request.form.get("price"))
        location = request.form.get("location")

        if not service_type or not price or not location:
            flash("Preencha todos os campos solicitados!")
            return redirect("/profile")

        elif price <= 0:
            flash("Preencha um valor maior do que R$00,00.")
            return redirect("/profile")

         # Verificar se o usuário já tem um serviço registrado
        if service:
            # Atualizar o serviço existente
            db.execute("""
                UPDATE services
                SET service_type = ?, price = ?, location = ?
                WHERE user_id = ?
            """, service_type, price, location, session["user_id"])
        else:
            # Inserir novo serviço
            db.execute("""
                INSERT INTO services (user_id, service_type, price, location)
                VALUES (?, ?, ?, ?)
            """, session["user_id"], service_type, price, location)

        return redirect("/search")

@app.route("/profile/<int:user_id>", methods=["GET", "POST"])
@login_required
def view_profile(user_id):
    # Obtenha as informações do prestador
    user = db.execute("""SELECT username, service_type, price, location
                      FROM users JOIN services ON users.id = services.user_id
                      WHERE users.id = ? AND users.role = 'Prestador de Serviço'""", user_id)

    if len(user) != 1:
        return apology("Prestador de serviço não encontrado!", 404)

    if request.method == "POST":
        rating = int(request.form.get("rating"))
        comment = str(request.form.get("comment"))
        db.execute("""INSERT INTO reviews
                   (provider_id, client_id, rating, comment)
                   VALUES (?, ?, ?, ?)""",
                   user_id, session["user_id"], rating, comment)
        flash("Avaliação registrada com sucesso.")
        return redirect("/search")
    # Obtenha as avaliações do prestador e a média de rating
    reviews = db.execute("SELECT client_id, rating, comment, created_at FROM reviews WHERE provider_id = ?", user_id)
    average_rating = db.execute("SELECT AVG(rating) as average FROM reviews WHERE provider_id = ?", user_id)[0]["average"]
    return render_template("view_profile.html", user=user[0], user_id=user_id, reviews=reviews, average_rating=average_rating)



@app.route("/rate_provider", methods=["GET", "POST"])
@login_required
def rate_provider():
    # Verifique se o usuário é um cliente
    client = db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])
    if client[0]["role"] != "Cliente":
        return apology("Apenas clientes podem avaliar prestadores de serviço.")


    if request.method == "POST":
        # Obtenha a avaliação e o comentário do formulário
        name = request.form.get("name")
        provider_info = db.execute("""SELECT id
                                   FROM users WHERE username = ? AND role = 'Prestador de Serviço'""", name)
        if provider_info:
            return redirect(f"/profile/{provider_info[0]['id']}")
        else:
            flash("Não há um prestador de serviço cadastrado com esse nome.")
            return redirect("/rate_provider")


    return render_template("rate_provider.html")


@app.route("/schedule", methods=["POST"])
@login_required
def schedule():
    if session["role"] == 'Prestador de Serviço':
        flash("Função apenas para clientes!")
        return redirect("/search")
    else:
        provider_id = request.form.get("provider_id")
        client_id = session["user_id"]
        service_date = request.form.get("service_date")

        db.execute("INSERT INTO appointments (client_id, provider_id, service_date) VALUES (?, ?, ?)",
                client_id, provider_id, service_date)
        flash("Agendamento solicitado com sucesso.")
        return redirect("/search")


@app.route("/provider_dashboard")
@login_required
def provider_dashboard():
    user = db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])
    if user[0]["role"] != "Prestador de Serviço":
        return apology("Essa função é apenas para Prestadores de Serviço!")

    pending_appointments = db.execute("SELECT * FROM appointments WHERE provider_id = ? AND status = 'pendente'", session["user_id"])
    all_appointments = db.execute("""SELECT appointments.id, client_id, provider_id,
                                  service_date, status, users.username
                                  FROM appointments JOIN users
                                  ON appointments.client_id = users.id
                                  WHERE provider_id = ? AND service_date > DATE('now') ORDER BY service_date
                                  """, session["user_id"])
    for appointment in all_appointments:
        appointment['service_date'] = datetime.strptime(appointment['service_date'], '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y %H:%M')
    return render_template("provider_dashboard.html", pending_appointments=pending_appointments, all_appointments=all_appointments)


@app.route("/update_appointment", methods=["POST"])
@login_required
def update_appointment():
    appointment_id = request.form.get("appointment_id")
    status = request.form.get("status")

    db.execute("UPDATE appointments SET status = ? WHERE id = ?", status, appointment_id)
    flash(f"Agendamento {status} com sucesso.")
    return redirect("/provider_dashboard")


@app.route("/history")
@login_required
def history():
    rows = db.execute("""SELECT appointments.id, client_id, provider_id,
                      service_date, status, users.username, services.service_type
                      FROM appointments JOIN users ON appointments.provider_id = users.id
                      JOIN services ON appointments.provider_id = services.user_id
                      WHERE client_id = ?
                      ORDER BY service_date""", session["user_id"])
    for appointment in rows:
        appointment['service_date'] = datetime.strptime(appointment['service_date'], '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y %H:%M')
    return render_template("history.html", rows=rows)


@app.route("/reset_data33")
@login_required
def reset_data():
    # Apaga registros das tabelas dependentes primeiro
    db.execute("DELETE FROM appointments")
    db.execute("DELETE FROM reviews")
    db.execute("DELETE FROM services")

    # Agora apaga a tabela users, pois não há mais dependências
    db.execute("DELETE FROM users")

    # Reinicia o contador de IDs (opcional)
    db.execute("DELETE FROM sqlite_sequence WHERE name='users'")
    db.execute("DELETE FROM sqlite_sequence WHERE name='services'")
    db.execute("DELETE FROM sqlite_sequence WHERE name='appointments'")
    db.execute("DELETE FROM sqlite_sequence WHERE name='reviews'")

    return "Dados apagados com sucesso."

@app.route("/put_data33")
@login_required
def insert_into_users():
    filepath = "users.csv"
    with open(filepath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            db.execute("""
                INSERT INTO users (username, email, password, role)
                VALUES (?, ?, ?, ?)
            """, row["username"], row["email"], generate_password_hash(row["password"]), row["role"])
    return "Dados INSERIDOS com sucesso."
