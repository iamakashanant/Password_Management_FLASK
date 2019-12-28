import logging
import uuid
from urllib.parse import urljoin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask import request, render_template, redirect, g, jsonify
from flask import url_for
from flask_appbuilder.security.sqla.models import User
from superset.models.user_attributes import UserAttribute
from superset import app, csrf, db
from superset.utils import emails

forgot_password_template = 'custom/users/forgot_password.html'
forgot_password_success_template = 'custom/users/forgot_password_success.html'
forgot_password_email_template = "custom/emails/password_reset.html"
reset_password_template = 'custom/users/reset_password.html'
reset_password_success_template = ''


logger = logging.getLogger(__name__)


@csrf.exempt
@app.route('/user/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    
    if request.method=='GET':
        return render_template(forgot_password_template)
    
    elif request.method=='POST':
        form_data=request.form.to_dict()
        # if form_data is None:
        #     return jsonify({"status": "error", "error_message": "No input data found"}), 400
        
        username = form_data.get('user')
        user_obj = db.session.query(User).filter_by(username=username).first() or None

       
        if user_obj is None:
            return jsonify({"status": "error", 'error_message': 'User not found'}), 400

        else:
            
            id=uuid.uuid4().int
            OTP=int(str(id)[:4])
            user_attr_obj=db.session.query(UserAttribute).filter_by(user_id=user_obj.id).first()
            user_attr_obj.reset_password_token=OTP
            user_attr_obj.reset_password_till=datetime.now() + timedelta(days=1)
            db.session.add(user_attr_obj)
            db.session.commit()

            emails.send_email(
                subject="OTP for Reset Password",
                recipients=[user_obj.email],
                template_path=forgot_password_email_template,
                context={'OTP': OTP})
            return redirect(url_for('reset_password'))
        return redirect(url_for('reset_password'))




@csrf.exempt
@app.route('/user/reset_password', methods=["GET", "POST"])
def reset_password():
    

    if request.method=='GET':
        return render_template(reset_password_template)

    elif request.method=="POST":
        
        data=request.form.to_dict()
        OTP=data.get('otp')


        user_attr_obj=db.session.query(UserAttribute).filter_by(reset_password_token=OTP).first() or None
        
        if user_attr_obj is None:
            return jsonify({"error_message": "OTP is invalid"}), 400
        print(user_attr_obj.reset_password_till)
        if user_attr_obj.reset_password_till <  datetime.now():
            return jsonify({"error_message": "OTP has expired. Try again"}), 400

        user = db.session.query(User).filter_by(id=user_attr_obj.user_id).first() or None
        if user is None:
            return jsonify({"error_message": "User not found"}), 400


        password = data.get('password')
        if not all([type(password) == str,  4 <= len(password) <= 20]):
            return jsonify({"error_message": "Password should be between 4 to 20 characters"}), 400

        try:
            user.password = generate_password_hash(password)
            db.session.add(user)
            user_attr_obj.reset_password_token = None
            user_attr_obj.reset_password_till = None
            db.session.add(user_attr_obj)
            db.session.commit()
        
        except Exception as e:
            logging.exception(e)
            return jsonify({"error_message": "Password could not be reset."}), 400

        return jsonify({"success": "Password reset successful"}), 200



        # if user.form.validate_on_submit():
        #     user.password=generate_password_hash(password)


###########################################################################################################

#--------------------------------------DON'T DELETE THE BELOW COMMENTED PART...............................
#-------------------------------------------ASK BEFORE EDITING----------------------------------------

###########################################################################################################



# @csrf.exempt
# @app.route('/user/forgot_password', methods=['GET', 'POST'])
# def forgot_password():
#     if g.user.is_authenticated:
#         return redirect('/')

#     if request.method == 'GET':
#         if 'success' in request.args:
#             return render_template(forgot_password_success_template)
#         return render_template(forgot_password_template)

#     elif request.method == 'POST':
#         form_data = request.form.to_dict()
#         if not form_data:
#             return jsonify({"status": "error", "error_message": "No input data found"}), 400

#         username = form_data.get('user')
#         user_obj = db.session.query(User).filter_by(username=username).first() or None
#         if user_obj is None:
#             return jsonify({"status": "error", 'error_message': 'User not found'}), 400

#         if user_obj.is_active is False:
#             return jsonify({'status': 'error', 'error_message': 'User account is inactive'}), 400

#         try:
#             # Generate token and save it in user_attribute table
#             token = uuid.uuid4()
#             user_attr_obj = db.session.query(UserAttribute).filter_by(user_id=user_obj.id).first()
#             user_attr_obj.reset_password_token = token
#             user_attr_obj.reset_password_till = datetime.now() + timedelta(days=2)
#             db.session.add(user_attr_obj)
#             db.session.commit()

#             password_reset_url = urljoin(request.url_root, url_for('reset_password')) + f"?token={token}"
#             emails.send_email(
#                 subject="Reset Password Email",
#                 recipients=[user_obj.email],
#                 template_path=forgot_password_email_template,
#                 context={'password_reset_url': password_reset_url}
#             )
#             return redirect(f"{request.url}?success=True")

#         except Exception as e:
#             logger.exception(e)
#             return jsonify({'status': 'error', 'error_message': 'Retry again'}), 400


# @csrf.exempt
# @app.route('/user/reset_password', methods=['GET', 'POST'])
# def reset_password():/
#     # If user is authenticated, redirect to homepage
#     if g.user.is_authenticated:
#         return redirect('/')

#     # Return template pages
#     if request.method == 'GET':
#         if 'success' in request.args:
#             return render_template(reset_password_success_template)

#         token = request.args.get('token')   
#         if bool(token) is False:
#             return redirect(url_for('forgot_password'))

#         return render_template(reset_password_template)

#     # Reset password form, validate form & reset password
#     elif request.method == 'POST':
#         data = request.form.to_dict()
#         token = data.get('token')
#         if bool(token) is False:
#             return jsonify({"error_message": "Token is missing"}), 400

#         password = data.get('password')
#         if bool(password) is False:
#             return jsonify({"error_message": "Password is missing"}), 400

#         user_attr_obj = db.session.query(UserAttribute).filter_by(reset_password_token=token).first() or None
#         if user_attr_obj is None:
#             return jsonify({"error_message": "Token is invalid"}), 400

#         # Validate if token is active
#         if user_attr_obj.reset_password_till < datetime.now():
#             return jsonify({"error_message": "Token has expired. Try again"}), 400

#         user = db.session.query(User).filter_by(id=user_attr_obj.user_id).first() or None
#         if user is None:
#             return jsonify({"error_message": "User not found"}), 400

#         # Validate password according to rules
#         if not all([
#             type(password) == str,  # password should be a string
#             4 <= len(password) <= 20  # password should be between 4 to 20 characters
#         ]):
#             return jsonify({"error_message": "Password should be between 4 to 20 characters"}), 400

#         try:
#             user.password = generate_password_hash(password)
#             db.session.add(user)
#             user_attr_obj.reset_password_token = None
#             user_attr_obj.reset_password_till = None

#             db.session.add(user_attr_obj)

#             db.session.commit()
#         except Exception as e:
#             logging.exception(e)
#             return jsonify({"error_message": "Password could not be reset."}), 400

#         return jsonify({"success": "Password reset successful"}), 200
