from flask import Flask, request

app = Flask(__name__)

@app.route('/reward')
def reward():
    points = request.args.get('points', '0')
    
    html_code = f"""
    <html>
    <head>
        <title>Thesis Reward</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #e8f5e9; }}
            .container {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); display: inline-block; width: 85%; max-width: 400px; border-top: 5px solid #4CAF50; }}
            h1 {{ color: #2E7D32; font-size: 24px; }}
            h2 {{ color: #4CAF50; font-size: 60px; margin: 10px 0; }}
            p {{ color: #555; font-size: 18px; line-height: 1.5; }}
            .footer {{ margin-top: 20px; font-size: 14px; color: #888; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AUTOMATED WASTE MONITORING</h1>
            <p>Congratulations! You earned:</p>
            <h2>{points}</h2>
            <p>Points!</p>
            <p class="footer">Thank you for recycling and saving the environment.</p>
        </div>
    </body>
    </html>
    """
    return html_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
