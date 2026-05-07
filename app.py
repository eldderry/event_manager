from flask import Flask, render_template, request, redirect, url_for
from models import db, Event
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ALLOWED_CATEGORIES = ['Конференция', 'Встреча', 'Вечеринка', 'Спорт']

db.init_app(app)

with app.app_context():
    db.create_all()


def parse_event_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def validate_event_form(form):
    title = form.get('title', '').strip()
    description = form.get('description', '').strip()
    date_str = form.get('date', '').strip()
    location = form.get('location', '').strip()
    category = form.get('category', '').strip()

    errors = []
    if not title:
        errors.append('Название обязано.')
    elif len(title) > 100:
        errors.append('Название не может быть длиннее 100 символов.')

    if not date_str:
        errors.append('Дата обязательна.')
    else:
        date = parse_event_date(date_str)
        if not date:
            errors.append('Неверный формат даты. Используйте ГГГГ-ММ-ДД.')
    
    if not location:
        errors.append('Место проведения обязательно.')
    elif len(location) > 100:
        errors.append('Место проведения не может быть длиннее 100 символов.')

    if not category:
        errors.append('Категория обязательна.')
    elif category not in ALLOWED_CATEGORIES:
        errors.append('Неверная категория.')

    return errors, title, description, parse_event_date(date_str), location, category


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def events():
    all_events = Event.query.all()
    return render_template('events.html', events=all_events)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        errors, title, description, date, location, category = validate_event_form(request.form)
        if errors:
            return render_template('add_event.html', errors=errors, form_data=request.form)

        new_event = Event(
            title=title,
            description=description,
            date=date,
            location=location,
            category=category
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('events'))
    return render_template('add_event.html', form_data={})

@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    event = Event.query.get_or_404(id)
    if request.method == 'POST':
        errors, title, description, date, location, category = validate_event_form(request.form)
        if errors:
            return render_template('edit_event.html', event=event, errors=errors, form_data=request.form)

        event.title = title
        event.description = description
        event.date = date
        event.location = location
        event.category = category
        db.session.commit()
        return redirect(url_for('events'))
    return render_template('edit_event.html', event=event, form_data={})

@app.route('/delete_event/<int:id>', methods=['POST'])
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('events'))

if __name__ == '__main__':
    app.run(debug=True)