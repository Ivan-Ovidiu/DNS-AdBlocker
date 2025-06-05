from flask import Flask, jsonify, request, render_template_string
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_stats():
    """Extrag statisticile din fisierul dns_stats.json"""
    
    file = 'dns_stats.json'

    try:
        if os.path.exists(file):
            with open(file, 'r') as f:
                return json.load(f)
        else:
            return {
                "timestamp": datetime.now().isoformat(),
                "total_blocked": 0,
                "domains_in_blocklist": 0,
                "companies": {}
            }
    except Exception as e:
        logger.error(f"Eroare la citirea statisticilor: {e}")
        return {'error': str(e)}

def update_stats(endpoint, data=None):

    try:
        stats_data = get_stats()

        if 'error' not in stats_data:
            stats_data['timestamp'] = datetime.now().isoformat()  
            with open('dns_stats.json', 'w') as f:
                json.dump(stats_data, f, indent=2)

    except Exception as e:
        logger.error(f"Error updating stats: {e}")


def get_logs():
    """Extrag ultimele linii din fisierul de logs"""

    file = "dns_blocker.log"

    try:
        if os.path.exists(file):
            with open(file, 'r') as f:
                lines = f.readlines()[-50:]  # ultimele 50 de linii
                return lines
        else:
            return ["fisierul de log nu exista"]
    except Exception as e:
        return [f"eroare: {str(e)}"]


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Statistici Ad-Blocker</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
        }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { 
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 20px;
            text-align: center;
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px; 
        }
        .stat-card { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number { 
            font-size: 2em; 
            font-weight: bold; 
            color: #4CAF50; 
        }
        .stat-label { 
            color: #666; 
            margin-top: 5px; 
        }
        .api-section { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .endpoint { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 10px;
            border-left: 4px solid #4CAF50;
        }
        .method { 
            background: #4CAF50; 
            color: white; 
            padding: 2px 8px; 
            border-radius: 3px; 
            font-size: 0.8em;
            margin-right: 10px;
        }
        .refresh-btn { 
            background: #4CAF50; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 1em;
        }
        .refresh-btn:hover { background: #45a049; }
        h2 { color: #333; margin-top: 0; }
        .data-entries { max-height: 300px; overflow-y: auto; }
        .data-item { 
            padding: 8px; 
            border-bottom: 1px solid #eee; 
            display: flex; 
            justify-content: space-between;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DNS Adblocker</h1>
            <p>Statistici si API endpoints</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.get('total_blocked', 0) }}</div>
                <div class="stat-label">Total Blocat</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.get('domains_in_blocklist', 0) }}</div>
                <div class="stat-label">Domenii in Blocklist</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.get('companies', {})|length }}</div>
                <div class="stat-label">Companii blocate</div>
            </div>
        </div>
        
        <div class="api-section">
            <h2>API Endpoints:</h2>
            <div class="endpoint">
                <span class="method">GET</span>
                <strong>/</strong> - Pagina principala
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <strong>/logs</strong> - Logurile programului
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <strong>/api/stats</strong> - Statistici ca JSON
            </div>
        </div>
        
        <div class="api-section">
            <h2>Companii blocate</h2>
            <div class="data-entries">
                {% for company, count in stats.get('companies', {}).items() %}
                <div class="data-item">
                    <span>{{ company }}</span>
                    <strong>{{ count }} blocked</strong>
                </div>
                {% endfor %}
                {% if not stats.get('companies', {}) %}
                <div class="data-item">
                    <span>Nicio companie nu a fost blocata momentan</span>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

</body>
</html>
"""

LOGS_HTML ="""
<div class="api-section">
    <h2>Loguri recente</h2>
    <div id="log-entries" class="data-entries" style="background-color:#fff;">
        <p>Se încarca log-urile...</p>
    </div>
</div>

<script>
    // Încărcare log-uri prin API
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('log-entries');
            container.innerHTML = '';
            if (data.logs && data.logs.length > 0) {
                data.logs.forEach(line => {
                    const div = document.createElement('div');
                    div.className = 'data-item';
                    div.textContent = line;
                    container.appendChild(div);
                });
            } else {
                container.innerHTML = '<p>Nu sunt loguri disponibile.</p>';
            }
        })
        .catch(err => {
            document.getElementById('log-entries').innerHTML = '<p>Eroare la încarcarea logurilor.</p>';
            console.error(err);
        });
</script>

"""


@app.route('/')
def stats():
    """Transmit statisticile catre website"""

    try:

        update_stats('dashboard')
        stats_data = get_stats()
        return render_template_string(HTML_TEMPLATE, stats=stats_data) #codul site-ului impreuna cu datele afisate
    
    except Exception as e:
        logger.error(f"Eroare laaccesarea statisticilor {e}")
        return jsonify({'eroare': {e}}), 500


@app.route('/api/logs', methods=['GET'])
def api_logs():
    """Returnez ultimele 100 linii ca JSON"""
    try:
        file = "dns_blocker.log"
        if os.path.exists(file):
            with open(file, 'r') as f:
                loguri = f.readlines()[-100:]
        else:
            loguri = []

        return jsonify({'logs': loguri})

    except Exception as e:
        logger.error(f"Eroare la afișarea logurilor: {e}")
        return jsonify({'eroare': {e}}), 500

@app.route('/logs', methods=['GET'])
def view_logs():
    """Returnez pagina html cu logurile"""
    return render_template_string(LOGS_HTML)


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """API endpoint preluare statistici ca si json"""
    try:
        stats_data = get_stats()
        return jsonify(stats_data)
    except Exception as e:
        return jsonify({'eroare': {e}}), 500


#Erori
@app.errorhandler(404)
def not_found(error):
    """eroari 404 e"""
    return jsonify({'eroare': 'endpointul nu a fost gasit, inecercati unul valid din lista'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'eroare': 'Internal server error'}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)