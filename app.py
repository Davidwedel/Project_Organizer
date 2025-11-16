from flask import Flask, render_template, request, redirect, url_for
from models import db, Category, Type, Project, Supply, Roadblock, Comment
import os

app = Flask(__name__)

# Use absolute path for database in production
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'projects.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create database tables and seed defaults
with app.app_context():
    db.create_all()

    # Add default types if none exist
    if Type.query.count() == 0:
        default_types = ['maintenance', 'new', 'repair', 'upgrade']
        for type_name in default_types:
            db.session.add(Type(name=type_name))
        db.session.commit()

@app.route('/')
def index():
    categories = Category.query.order_by(Category.name).all()
    return render_template('index.html', categories=categories)

@app.route('/category/<int:category_id>')
def view_category(category_id):
    category = Category.query.get_or_404(category_id)
    projects = Project.query.filter_by(category_id=category_id).order_by(Project.created_at.desc()).all()
    return render_template('category.html', category=category, projects=projects)

@app.route('/project/new', methods=['GET', 'POST'])
@app.route('/category/<int:category_id>/project/new', methods=['GET', 'POST'])
def new_project(category_id=None):
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        tag = request.form.get('tag')
        implement = request.form.get('implement', '')
        information = request.form.get('information', '')

        project = Project(name=name, category_id=category_id, tag=tag, implement=implement, information=information)
        db.session.add(project)
        db.session.flush()  # Get project.id before adding related items

        # Add supplies (one per line)
        supplies_text = request.form.get('supplies', '')
        if supplies_text.strip():
            for line in supplies_text.strip().split('\n'):
                item = line.strip()
                if item:
                    supply = Supply(item=item, project_id=project.id)
                    db.session.add(supply)

        # Add initial comments
        comments_text = request.form.get('comments', '')
        if comments_text.strip():
            comment = Comment(text=comments_text.strip(), project_id=project.id)
            db.session.add(comment)

        db.session.commit()

        return redirect(url_for('view_project', project_id=project.id))

    categories = Category.query.order_by(Category.name).all()
    types = Type.query.order_by(Type.name).all()
    return render_template('new_project.html', categories=categories, types=types, selected_category_id=category_id)

@app.route('/project/<int:project_id>')
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    categories = Category.query.order_by(Category.name).all()
    types = Type.query.order_by(Type.name).all()
    return render_template('project.html', project=project, categories=categories, types=types)

@app.route('/project/<int:project_id>/edit', methods=['POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.name = request.form.get('name')
    project.category_id = request.form.get('category_id')
    project.tag = request.form.get('tag')
    project.implement = request.form.get('implement', '')
    project.information = request.form.get('information', '')
    db.session.commit()
    return redirect(url_for('view_project', project_id=project.id))

@app.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/project/<int:project_id>/supply/add', methods=['POST'])
def add_supply(project_id):
    project = Project.query.get_or_404(project_id)
    item = request.form.get('item')
    if item:
        supply = Supply(item=item, project_id=project.id)
        db.session.add(supply)
        db.session.commit()
    return redirect(url_for('view_project', project_id=project.id))

@app.route('/supply/<int:supply_id>/toggle', methods=['POST'])
def toggle_supply(supply_id):
    supply = Supply.query.get_or_404(supply_id)
    supply.checked = not supply.checked
    db.session.commit()
    return redirect(url_for('view_project', project_id=supply.project_id))

@app.route('/supply/<int:supply_id>/delete', methods=['POST'])
def delete_supply(supply_id):
    supply = Supply.query.get_or_404(supply_id)
    project_id = supply.project_id
    db.session.delete(supply)
    db.session.commit()
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/project/<int:project_id>/roadblock/add', methods=['POST'])
def add_roadblock(project_id):
    project = Project.query.get_or_404(project_id)
    description = request.form.get('description')
    if description:
        roadblock = Roadblock(description=description, project_id=project.id)
        db.session.add(roadblock)
        db.session.commit()
    return redirect(url_for('view_project', project_id=project.id))

@app.route('/roadblock/<int:roadblock_id>/delete', methods=['POST'])
def delete_roadblock(roadblock_id):
    roadblock = Roadblock.query.get_or_404(roadblock_id)
    project_id = roadblock.project_id
    db.session.delete(roadblock)
    db.session.commit()
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/project/<int:project_id>/comment/add', methods=['POST'])
def add_comment(project_id):
    project = Project.query.get_or_404(project_id)
    text = request.form.get('text')
    if text:
        comment = Comment(text=text, project_id=project.id)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('view_project', project_id=project.id))

@app.route('/help-wanted')
def help_wanted():
    roadblocks = Roadblock.query.join(Project).order_by(Project.name, Roadblock.created_at.desc()).all()
    return render_template('help_wanted.html', roadblocks=roadblocks)

@app.route('/supplies-needed')
def supplies_needed():
    supplies = Supply.query.join(Project).order_by(Project.name, Supply.created_at.desc()).all()
    return render_template('supplies_needed.html', supplies=supplies)

# Settings Routes
@app.route('/settings')
def settings():
    categories = Category.query.order_by(Category.name).all()
    types = Type.query.order_by(Type.name).all()
    return render_template('settings.html', categories=categories, types=types)

@app.route('/settings/category/add', methods=['POST'])
def add_category():
    name = request.form.get('name')
    if name:
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
    return redirect(url_for('settings'))

@app.route('/settings/category/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('settings'))

@app.route('/settings/type/add', methods=['POST'])
def add_type():
    name = request.form.get('name')
    if name:
        type_obj = Type(name=name)
        db.session.add(type_obj)
        db.session.commit()
    return redirect(url_for('settings'))

@app.route('/settings/type/<int:type_id>/delete', methods=['POST'])
def delete_type(type_id):
    type_obj = Type.query.get_or_404(type_id)
    db.session.delete(type_obj)
    db.session.commit()
    return redirect(url_for('settings'))

if __name__ == '__main__':
    app.run(debug=True, port=5003)
