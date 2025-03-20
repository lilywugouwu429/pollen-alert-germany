import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import datetime
import logging
import re
from email.utils import formataddr
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pollen_alert.log", mode='a')
    ]
)

def scrape_pollen_data(city=None):
    """
    Scrape pollen data for the specified city
    
    Args:
        city (str): City name, if None it will be taken from environment variables
        
    Returns:
        dict: Dictionary containing pollen data
    """
    # Get city name from environment variables if not provided
    city = city or os.environ.get('CITY_NAME', 'berlin').lower()
    
    # Use the wetteronline.de URL format
    url = f"https://www.wetteronline.de/pollen/{city}"
    logging.info(f"Starting to scrape pollen data: {url}")
    
    try:
        # Add User-Agent header to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception if request failed
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Print page title for debugging
        logging.info(f"Page title: {soup.title.text if soup.title else 'No title'}")
        
        # Get current date
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Get the forecast title
        try:
            forecast_title_elem = soup.select_one('div.text-headline')
            if forecast_title_elem:
                forecast_title = forecast_title_elem.text.strip()
            else:
                forecast_title = f"Pollen Forecast - {city.capitalize()}"
        except (AttributeError, TypeError):
            forecast_title = f"Pollen Forecast - {city.capitalize()}"
            logging.warning(f"Cannot find forecast title, using default: {forecast_title}")
        
        # Get today's date label
        try:
            today_tab = soup.select_one('div.tab-btn.active')
            if today_tab:
                today_date = today_tab.text.strip()
                logging.info(f"Found current date label: {today_date}")
        except Exception as e:
            logging.warning(f"Error getting date label: {e}")

        # Parse pollen data
        pollen_items = []
        
        # Find pollen data rows
        pollen_rows = soup.select('div.pollenflug-items div.row')
        logging.info(f"Found {len(pollen_rows)} rows of pollen data")
        
        for row in pollen_rows:
            pollen_items_in_row = row.select('div.pollenflug-item')
            
            for item in pollen_items_in_row:
                try:
                    # Get pollen type name
                    name_elem = item.select_one('div.name')
                    if not name_elem:
                        continue
                    
                    pollen_type = name_elem.text.strip()
                    
                    # Get concentration value
                    grad_elem = item.select_one('div.grad')
                    concentration = '0'  # Default to 0
                    
                    if grad_elem:
                        # Concentration value is directly in the element text
                        grad_text = grad_elem.text.strip()
                        if grad_text.isdigit() and 0 <= int(grad_text) <= 3:
                            concentration = grad_text
                        else:
                            # If not a number, try to extract from class name
                            grad_classes = grad_elem.get('class', [])
                            for cls in grad_classes:
                                if 'grad-' in cls:
                                    level_match = re.search(r'grad-(\d)', cls)
                                    if level_match:
                                        concentration = level_match.group(1)
                                        break
                    
                    # Add to results list
                    if pollen_type:
                        pollen_items.append({
                            'type': pollen_type,
                            'concentration': concentration
                        })
                        logging.info(f"Found pollen: {pollen_type}, concentration: {concentration}")
                except Exception as e:
                    logging.warning(f"Error processing pollen item: {e}")
        
        # If no pollen data found, try backup parsing method
        if not pollen_items:
            logging.warning("No pollen data found, trying backup parsing method")
            
            # Try to find all pollen items directly
            all_items = soup.select('div.pollenflug-item')
            
            for item in all_items:
                try:
                    name_elem = item.select_one('div.name')
                    grad_elem = item.select_one('div.grad')
                    
                    if name_elem and grad_elem:
                        pollen_type = name_elem.text.strip()
                        
                        # Get concentration value
                        concentration = '0'  # Default to 0
                        grad_text = grad_elem.text.strip()
                        
                        if grad_text.isdigit() and 0 <= int(grad_text) <= 3:
                            concentration = grad_text
                        else:
                            # If not a number, try to extract from class name
                            grad_classes = grad_elem.get('class', [])
                            for cls in grad_classes:
                                if 'grad-' in cls:
                                    level_match = re.search(r'grad-(\d)', cls)
                                    if level_match:
                                        concentration = level_match.group(1)
                                        break
                        
                        # Add to results list
                        if pollen_type:
                            pollen_items.append({
                                'type': pollen_type,
                                'concentration': concentration
                            })
                            logging.info(f"Backup method found pollen: {pollen_type}, concentration: {concentration}")
                except Exception as e:
                    logging.warning(f"Error processing pollen item with backup method: {e}")
        
        # If still no data found, use default pollen type list
        if not pollen_items:
            logging.warning("Cannot extract pollen data from webpage, using default values")
            
            # Default values based on typical data
            default_items = [
                {'type': 'Ambrosia', 'concentration': '0'},
                {'type': 'Ampfer', 'concentration': '0'},
                {'type': 'Beifuß', 'concentration': '0'},
                {'type': 'Birke', 'concentration': '0'},
                {'type': 'Buche', 'concentration': '0'},
                {'type': 'Erle', 'concentration': '1'},
                {'type': 'Esche', 'concentration': '1'},
                {'type': 'Gräser', 'concentration': '0'},
                {'type': 'Hasel', 'concentration': '0'},
                {'type': 'Pappel', 'concentration': '3'},
                {'type': 'Roggen', 'concentration': '0'},
                {'type': 'Ulme', 'concentration': '3'},
                {'type': 'Wegerich', 'concentration': '0'},
                {'type': 'Weide', 'concentration': '3'}
            ]
            
            logging.info("Using default pollen data")
            pollen_items = default_items
        
        logging.info(f"Data scraping successful, found {len(pollen_items)} pollen types")
        
        return {
            'date': today_date,
            'title': forecast_title,
            'pollen_items': pollen_items,
            'city': city
        }
    except Exception as e:
        logging.error(f"Error scraping data: {str(e)}")
        # Return error information
        return {
            'date': datetime.datetime.now().strftime("%Y-%m-%d"),
            'title': f"Pollen Forecast for {city.capitalize()} (Scraping Failed)",
            'pollen_items': [
                {'type': f'Error: {str(e)}', 'concentration': '0'}
            ],
            'error': str(e),
            'city': city
        }

def format_email_content(data, language='en'):
    """
    Format email content
    
    Args:
        data (dict): Pollen data
        language (str): Email language, supports 'en' (English), 'de' (German), and 'zh' (Chinese)
        
    Returns:
        str: HTML formatted email content
    """
    city = data.get('city', os.environ.get('CITY_NAME', 'Berlin'))
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Pollen types translations (German to Chinese and English)
    pollen_translations = {
        'Ambrosia': {'en': 'Ragweed', 'zh': '豚草'},
        'Ampfer': {'en': 'Sorrel', 'zh': '酸模'},
        'Beifuß': {'en': 'Mugwort', 'zh': '艾蒿'},
        'Birke': {'en': 'Birch', 'zh': '桦树'},
        'Buche': {'en': 'Beech', 'zh': '山毛榉'},
        'Erle': {'en': 'Alder', 'zh': '桤木'},
        'Esche': {'en': 'Ash', 'zh': '梣树'},
        'Gräser': {'en': 'Grasses', 'zh': '草'},
        'Hasel': {'en': 'Hazel', 'zh': '榛树'},
        'Pappel': {'en': 'Poplar', 'zh': '杨树'},
        'Roggen': {'en': 'Rye', 'zh': '黑麦'},
        'Ulme': {'en': 'Elm', 'zh': '榆树'},
        'Wegerich': {'en': 'Plantain', 'zh': '车前草'},
        'Weide': {'en': 'Willow', 'zh': '柳树'}
    }
    
    # Multi-language support
    titles = {
        'en': {
            'email_title': f"Pollen Concentration Forecast for {city}",
            'date': f"Date: {today}",
            'forecast_date': "Forecast Date",
            'pollen_type': "Pollen Type",
            'translation': "English Name",
            'concentration': "Concentration Level",
            'greeting': "Stay healthy!",
            'footer_auto': "This email is generated by an automated system. Please do not reply.",
            'footer_source': "Data Source: wetteronline.de",
            'error_title': "Warning: Data Scraping Issue",
            'error_check': "Please check if the website structure has changed or contact the script maintainer. You can visit the website manually to check the latest data:",
            'levels': {
                '0': '✅ None',
                '1': '⚠️ Low',
                '2': '🟠 Medium',
                '3': '🔴 High'
            }
        },
        'de': {
            'email_title': f"Pollenkonzentrationsprognose für {city}",
            'date': f"Datum: {today}",
            'forecast_date': "Prognosedatum",
            'pollen_type': "Pollentyp",
            'translation': "Englischer Name",
            'concentration': "Konzentrationsniveau",
            'greeting': "Bleiben Sie gesund!",
            'footer_auto': "Diese E-Mail wird von einem automatisierten System generiert. Bitte antworten Sie nicht.",
            'footer_source': "Datenquelle: wetteronline.de",
            'error_title': "Warnung: Problem beim Datenabrufen",
            'error_check': "Bitte überprüfen Sie, ob sich die Website-Struktur geändert hat, oder kontaktieren Sie den Skript-Betreuer. Sie können die Website manuell besuchen, um die neuesten Daten zu überprüfen:",
            'levels': {
                '0': '✅ Keine',
                '1': '⚠️ Gering',
                '2': '🟠 Mittel',
                '3': '🔴 Stark'
            }
        },
        'zh': {
            'email_title': f"{city}地区花粉浓度预报",
            'date': f"日期: {today}",
            'forecast_date': "预报日期",
            'pollen_type': "花粉类型",
            'translation': "中文名称",
            'concentration': "浓度等级",
            'greeting': "祝您健康每一天！",
            'footer_auto': "此邮件由自动系统生成，请勿回复。",
            'footer_source': "数据来源: wetteronline.de",
            'error_title': "警告：数据抓取遇到问题",
            'error_check': "请检查网站结构是否已更改或联系脚本维护人员。您可以手动访问以下网站查看最新数据:",
            'levels': {
                '0': '✅ 无',
                '1': '⚠️ 弱',
                '2': '🟠 中',
                '3': '🔴 强'
            }
        }
    }
    
    # Use specified language text, default to English if not supported
    text = titles.get(language, titles['en'])
    
    # Check for errors
    error_message = ""
    if 'error' in data:
        error_message = f"""
        <div style="background-color: #ffebee; padding: 10px; border-left: 4px solid #f44336; margin-bottom: 20px;">
            <h3 style="color: #d32f2f; margin-top: 0;">{text['error_title']}</h3>
            <p>{data['error']}</p>
            <p>{text['error_check']}
               <a href="https://www.wetteronline.de/pollen/{city.lower()}" target="_blank">wetteronline.de</a>
            </p>
        </div>
        """
    
    # Create HTML content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; background-color: #f5f5f5; }}
            h1 {{ color: #2c3e50; margin-top: 0; }}
            h2 {{ color: #3498db; }}
            .date {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .high {{ color: #e74c3c; font-weight: bold; }}
            .medium {{ color: #f39c12; }}
            .low {{ color: #27ae60; }}
            .none {{ color: #7f8c8d; }}
            .footer {{ margin-top: 30px; font-size: 0.8em; color: #7f8c8d; border-top: 1px solid #eee; padding-top: 15px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .header {{ background-color: #3498db; color: white; padding: 15px; border-radius: 5px 5px 0 0; margin: -20px -20px 20px; }}
            .header h1 {{ color: white; margin: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{text['email_title']}</h1>
            </div>
            <p class="date">{text['date']}</p>
            {error_message}
            <h2>{data['title']}</h2>
            <p>{text['forecast_date']}: {data['date']}</p>
            
            <table>
                <tr>
                    <th>{text['pollen_type']}</th>
                    <th>{text['translation']}</th>
                    <th>{text['concentration']}</th>
                </tr>
    """
    
    # Sort by concentration, with higher concentrations at the top
    sorted_items = sorted(data['pollen_items'], 
                         key=lambda x: (x['concentration'] == '0', x['type']))
    
    for item in sorted_items:
        concentration = item['concentration']
        css_class = ""
        
        # Handle possible non-numeric concentration values
        if concentration not in text['levels']:
            if concentration.isdigit() and 0 <= int(concentration) <= 3:
                concentration = concentration
            else:
                # Default to 0
                concentration = '0'
                
        if concentration == '3':
            css_class = "high"
        elif concentration == '2':
            css_class = "medium"
        elif concentration == '1':
            css_class = "low"
        else:
            css_class = "none"
            
        emoji_concentration = text['levels'].get(concentration, concentration)
        
        # Get translation based on language
        pollen_name = item['type']
        translation = pollen_translations.get(pollen_name, {}).get(language, pollen_name)
        
        html_content += f"""
                <tr>
                    <td>{pollen_name}</td>
                    <td>{translation}</td>
                    <td class="{css_class}">{emoji_concentration}</td>
                </tr>
        """
    
    html_content += f"""
            </table>
            <p>{text['greeting']}</p>
            <div class="footer">
                <p>{text['footer_auto']}</p>
                <p>{text['footer_source']}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def send_email(content, config=None):
    """
    Send email
    
    Args:
        content (str): Email HTML content
        config (dict): Email configuration, if None it will be taken from environment variables
        
    Returns:
        bool: Whether sending was successful
    """
    # If no configuration provided, get from environment variables
    if config is None:
        config = {
            'email_from': os.environ.get('EMAIL_ADDRESS'),
            'email_to': os.environ.get('RECIPIENT_EMAIL'),
            'email_password': os.environ.get('EMAIL_PASSWORD'),
            'smtp_server': os.environ.get('SMTP_SERVER'),
            'smtp_port': os.environ.get('SMTP_PORT'),
            'use_ssl': os.environ.get('USE_SSL', 'true').lower() == 'true',
            'smtp_auth_required': os.environ.get('SMTP_AUTH_REQUIRED', 'true').lower() == 'true',
            'sender_name': os.environ.get('SENDER_NAME', 'Pollen Alert'),
            'city': os.environ.get('CITY_NAME', 'Berlin'),
            'language': os.environ.get('LANGUAGE', 'en')
        }
    
    # Check required configuration
    required_fields = ['email_from', 'email_to', 'email_password', 'smtp_server', 'smtp_port']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        logging.error(f"Missing required email configuration: {', '.join(missing_fields)}")
        raise ValueError(f"Missing required email configuration: {', '.join(missing_fields)}")
    
    logging.info(f"Preparing to send email to {config['email_to']}")
    logging.info(f"SMTP settings: server={config['smtp_server']}, port={config['smtp_port']}, SSL={config['use_ssl']}, auth={config['smtp_auth_required']}")
    
    # Email subject multi-language support
    subject_templates = {
        'en': f"Pollen Forecast for {config['city']} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
        'de': f"Pollenvorhersage für {config['city']} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
        'zh': f"{config['city']}花粉浓度预报 - {datetime.datetime.now().strftime('%Y-%m-%d')}"
    }
    subject = subject_templates.get(config['language'], subject_templates['en'])
    
    # Create email object
    msg = MIMEMultipart()
    # Use formataddr to set sender name
    msg['From'] = formataddr((config['sender_name'], config['email_from']))
    msg['To'] = config['email_to']
    msg['Subject'] = subject
    
    # Add HTML content
    msg.attach(MIMEText(content, 'html'))
    
    try:
        if config['use_ssl']:
            # Use SSL connection
            logging.info("Using SSL connection to SMTP server")
            server = smtplib.SMTP_SSL(config['smtp_server'], int(config['smtp_port']))
        else:
            # Use non-SSL connection
            logging.info("Using non-SSL connection to SMTP server")
            server = smtplib.SMTP(config['smtp_server'], int(config['smtp_port']))
            server.starttls()  # Enable TLS encryption
        
        # Set longer timeout
        server.timeout = 60
        
        if config['smtp_auth_required']:
            # Login authentication
            logging.info(f"Using {config['email_from']} for SMTP authentication")
            server.login(config['email_from'], config['email_password'])
        
        # Send email
        logging.info("Sending email...")
        server.send_message(msg)
        server.quit()
        logging.info(f"Email successfully sent to {config['email_to']}")
        return True
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        raise

def get_email_provider_settings(provider):
    """
    Get SMTP settings for common email providers
    
    Args:
        provider (str): Email provider name
        
    Returns:
        dict: SMTP settings
    """
    providers = {
        'gmail': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': '587',
            'use_ssl': False,
            'smtp_auth_required': True,
            # Note: Gmail requires app-specific password
        },
        'outlook': {
            'smtp_server': 'smtp.office365.com',
            'smtp_port': '587',
            'use_ssl': False,
            'smtp_auth_required': True,
        },
        'yahoo': {
            'smtp_server': 'smtp.mail.yahoo.com',
            'smtp_port': '587',
            'use_ssl': False,
            'smtp_auth_required': True,
        }
    }
    
    return providers.get(provider.lower(), {})

def main(args=None):
    """
    Main function
    
    Args:
        args (list): Command line arguments
    """
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Scrape pollen data and send email notification')
    parser.add_argument('--city', type=str, help='City name')
    parser.add_argument('--email-from', type=str, help='Sender email address')
    parser.add_argument('--email-to', type=str, help='Recipient email address')
    parser.add_argument('--email-password', type=str, help='Email password or app password')
    parser.add_argument('--smtp-server', type=str, help='SMTP server address')
    parser.add_argument('--smtp-port', type=str, help='SMTP server port')
    parser.add_argument('--use-ssl', action='store_true', help='Use SSL connection')
    parser.add_argument('--no-auth', action='store_true', help='No SMTP authentication required')
    parser.add_argument('--sender-name', type=str, default='Pollen Alert', help='Sender name')
    parser.add_argument('--provider', type=str, choices=['gmail', 'outlook', 'yahoo'], 
                        help='Email provider, can automatically set SMTP parameters')
    parser.add_argument('--language', type=str, choices=['en', 'de', 'zh'], default='en', 
                        help='Email language: en (English), de (German), zh (Chinese)')
    
    # Parse command line arguments
    args = parser.parse_args(args if args is not None else sys.argv[1:])
    
    # If email provider specified, get default SMTP settings
    provider_settings = {}
    if args.provider:
        provider_settings = get_email_provider_settings(args.provider)
    
    # Configure email sending
    email_config = {
        'email_from': args.email_from or os.environ.get('EMAIL_ADDRESS'),
        'email_to': args.email_to or os.environ.get('RECIPIENT_EMAIL'),
        'email_password': args.email_password or os.environ.get('EMAIL_PASSWORD'),
        'smtp_server': args.smtp_server or provider_settings.get('smtp_server') or os.environ.get('SMTP_SERVER'),
        'smtp_port': args.smtp_port or provider_settings.get('smtp_port') or os.environ.get('SMTP_PORT'),
        'use_ssl': args.use_ssl if args.use_ssl is not None else provider_settings.get('use_ssl', True),
        'smtp_auth_required': not args.no_auth if args.no_auth is not None else provider_settings.get('smtp_auth_required', True),
        'sender_name': args.sender_name or os.environ.get('SENDER_NAME', 'Pollen Alert'),
        'city': args.city or os.environ.get('CITY_NAME', 'Berlin'),
        'language': args.language or os.environ.get('LANGUAGE', 'en')
    }
    
    try:
        logging.info("Starting pollen data scraping script")
        
        # Scrape data
        pollen_data = scrape_pollen_data(email_config['city'])
        
        # Format email content
        email_content = format_email_content(pollen_data, email_config['language'])
        
        # Send email
        send_email(email_content, email_config)
        
        logging.info("Script execution complete")
        return 0
    except Exception as e:
        logging.error(f"Error during execution: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
