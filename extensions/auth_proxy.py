from zipfile import ZipFile
import os

# def create_proxy_extension(proxy):
#     proxy_host = proxy['ip']
#     proxy_port = proxy['port']
#     username = proxy['user']
#     password = proxy['pass']
    
#     output_dir = '/extensions/'
#     os.makedirs(output_dir, exist_ok=True)
    
#     output_file = f'extensions/{proxy_host.replace(".", "_")}.zip'
    
#     """
#     Tạo extension Chrome hỗ trợ proxy.
    
#     Args:
#         proxy_host (str): Địa chỉ IP hoặc hostname của proxy.
#         proxy_port (int): Cổng của proxy.
#         username (str): Tên người dùng proxy.
#         password (str): Mật khẩu proxy.
#         output_file (str): Tên file zip chứa extension (mặc định là 'proxy_auth_plugin_v3.zip').
    
#     Returns:
#         str: Đường dẫn tới file zip vừa tạo.
#     """
#     manifest_json = """
#     {
#         "version": "1.0.0",
#         "manifest_version": 3,
#         "name": "Proxy Authentication",
#         "permissions": [
#             "proxy",
#             "storage",
#             "webRequest",
#             "webRequestAuthProvider"
#         ],
#         "host_permissions": ["<all_urls>"],
#         "background": {
#             "service_worker": "background.js"
#         }
#     }
#     """
    
#     background_js = f"""
#     chrome.proxy.settings.set({{
#         value: {{
#             mode: "fixed_servers",
#             rules: {{
#                 singleProxy: {{
#                     scheme: "http",
#                     host: "{proxy_host}",
#                     port: parseInt({proxy_port})
#                 }},
#                 bypassList: ["localhost"]
#             }}
#         }},
#         scope: "regular"
#     }}, function() {{
#         console.log("Proxy configuration set.");
#     }});

#     chrome.webRequest.onAuthRequired.addListener(
#         function(details) {{
#             return {{
#                 authCredentials: {{
#                     username: "{username}",
#                     password: "{password}"
#                 }}
#             }};
#         }},
#         {{ urls: ["<all_urls>"] }},
#         ["blocking"]
#     );
#     """
    
#     # Tạo file zip chứa extension
#     with ZipFile(output_file, 'w') as zp:
#         zp.writestr("manifest.json", manifest_json)
#         zp.writestr("background.js", background_js)
    
#     return output_file


from zipfile import ZipFile
import os

def create_proxy_extension(proxy):
    proxy_host = proxy['ip']
    proxy_port = proxy['port']
    username = proxy['user']
    password = proxy['pass']
    
    output_dir = '/extensions/'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f'extensions/{proxy_host.replace(".", "_")}.xpi'
    
    manifest_json = """
    {
        "manifest_version": 2,
        "name": "Proxy Authentication",
        "version": "1.0",
        "permissions": [
            "proxy",
            "storage",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"],
            "persistent": false
        },
        "browser_action": {
            "default_popup": "popup.html"
        }
    }
    """
    
    background_js = f"""
    browser.proxy.onRequest.addListener(
        function(details) {{
            return {{
                authCredentials: {{
                    username: "{username}",
                    password: "{password}"
                }}
            }};
        }},
        {{ urls: ["<all_urls>"] }},
        ["blocking"]
    );
    
    browser.proxy.settings.set({{
        value: {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: {proxy_port}
                }},
                bypassList: ["localhost"]
            }}
        }},
        scope: "regular"
    }});
    """

    # Tạo file .xpi chứa extension cho Firefox
    with ZipFile(output_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    
    return output_file
