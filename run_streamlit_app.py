import subprocess

command = 'streamlit run nba_shots_viz_project_st_app.py'
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Run a cmd command

output, error = process.communicate()  # Get the output and error, if any
print(output.decode())  # Print the output
if error:  # Print the error, if any
    print(error.decode())
