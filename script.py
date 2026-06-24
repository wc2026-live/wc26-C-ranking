from datetime import datetime

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>World Cup Live Ranking</title>
</head>
<body>
    <h1>World Cup Live Ranking</h1>
    <p>Updated: {datetime.now()}</p>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
