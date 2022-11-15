from flask import Flask, render_template,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import smtplib, ssl,email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # ///- relative path, //// - absolute path
db=SQLAlchemy(app)

class Todo(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created =db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['POST','GET'])
def index():
    if request.method=='POST':
        task_content=request.form['content']
        new_task = Todo(content =task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "there was error"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)



@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete=Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "unable to delete"

@app.route("/update/<int:id>", methods=['GET','POST'])
def update(id):
    task=Todo.query.get_or_404(id)

    if request.method=='POST':
        task.content=request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "there was error"
    else:
        # tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('update.html',task=task)

@app.route("/email", methods=['GET','POST'])
def email():
    if request.method=='POST':
        emails=request.form['emails']
        email_list=emails.split(',')
        subject=request.form['subject']
        body=request.form['body']
        sender_email = request.form['sender_email']
        if len(request.form['password'])==0:
            password = 'yyhilkdpsucwtijg'
        else:
            password = request.form['password']

        try:
            for i in email_list:
                
                receiver_email = i
                # password = input("Type your password and press enter:")
                # Create a multipart message and set headers
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = subject
            #     message["Bcc"] = receiver_email  # Recommended for mass emails

                # Add body to email
                message.attach(MIMEText(body, "plain"))

                filename = "Trupti.pdf"  # In same directory as script

                # Open PDF file in binary mode
                with open(filename, "rb") as attachment:
                    # Add file as application/octet-stream
                    # Email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                # Encode file in ASCII characters to send by email    
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )

                # Add attachment to message and convert message to string
                message.attach(part)
                text = message.as_string()

                # Log in to server using secure context and send email
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, text)
                flash("All the emails have been successfully sent")
            return redirect('/')
        except:
            return "All fields are mandetory"
    else:
        return render_template('email.html')

if __name__=="__main__":
    app.run(debug=True)