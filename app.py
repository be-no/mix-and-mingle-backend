from flask import Flask, request, send_file, jsonify
import pandas as pd
import itertools # for permutations
from io import BytesIO
from models import Output

app = Flask(__name__)

# GET NEW
@app.route('/api/upload', methods=['POST'])
def upload():
    # getting uploaded file from frontend
    df_input = pd.read_excel(request.files['file'])
    names_column = df_input['Names']
    perms = list(itertools.permutations(names_column))
    df_perms = pd.DataFrame(perms)

    output_data = BytesIO()
    df_perms.to_excel(output_data, index=False)
    output_data.seek(0)
    Output.create(file_data=output_data.getvalue())
    
    message = {'message': 'Your mix is now ready in "See All Mixes"!'}
    return jsonify(message), 200

# POST CREATE
@app.route('/api/download', methods=['GET'])
def download():
    # Retrieve the latest output file data from the SQLite database
    latest_output = Output.select().order_by(Output.id.desc()).first()
    if latest_output:
        file_data = latest_output.file_data

        # Create a BytesIO object to serve the file data
        output_file = BytesIO(file_data)

        return send_file(output_file, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # If no output file is found, return an error response
    return jsonify({'error': 'No output file found'}), 404

# GET INDEX
# edit function so each file has a different name
@app.route('/api/files', methods=['GET'])
def get():
    files = Output.select().execute()
    file_list = [{'id': file.id, 'name': file.name} for file in files]
    return jsonify(file_list)

# GET EDIT / PUT UPDATE
# route for user to update name of a specific file
@app.route('/api/files/<int:file_id>', methods=['PATCH'])
def update(file_id):
    new_name = request.json.get('name')

    file = Output.get_by_id(file_id)
    file.name = new_name
    file.save()

    return jsonify({'message': 'File name updated successfully'})

# GET DELETE
@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        file = Output.select().where(Output.id == file_id).first()
        if file:
            file.delete_instance()
            return jsonify({'message': 'File deleted successfully'})
        else:
            return jsonify({'message': 'File not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run()