# Pollen Forecast Email Alert

![Pollen Alert](https://img.shields.io/badge/Pollen-Alert-green)
![Language](https://img.shields.io/badge/Language-Python-blue)
![License](https://img.shields.io/badge/License-MIT-orange)

This project uses GitHub Actions to automatically scrape pollen concentration data from [wetteronline.de](https://www.wetteronline.de/pollen/) and send daily email notifications. Perfect for people with pollen allergies who want to monitor local pollen levels.

## Features

- 🌱 Automatically fetches pollen forecast data for specified cities
- 📊 Displays concentration levels for different pollen types in an intuitive format
- 📧 Supports multiple email service providers (Gmail, Outlook, Yahoo)
- 🌐 Multi-language support (English and German)
- 🔄 Configurable for daily automatic updates
- 📱 Beautiful HTML email format, mobile-friendly
- 🔧 Highly customizable with command-line arguments and environment variables

## Setup Guide

### 1. Fork this repository

First, click the "Fork" button in the top right corner of this repository to create a copy in your GitHub account.

### 2. Configure GitHub Secrets

In your forked repository, you need to set up the following GitHub Secrets for email delivery:

1. Go to your forked repository
2. Click "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret" and add the following secrets:

Required secrets:
- `EMAIL_ADDRESS`: Your email address (sender)
- `RECIPIENT_EMAIL`: The email address that will receive the notifications
- `EMAIL_PASSWORD`: Your email password or app-specific password
- `SMTP_SERVER`: SMTP server address (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (e.g., 587 or 465)

Optional secrets:
- `CITY_NAME`: City name (default is "berlin")
- `USE_SSL`: Whether to use SSL connection (true or false)
- `SMTP_AUTH_REQUIRED`: Whether SMTP authentication is required (true or false)
- `SENDER_NAME`: Sender name (default is "Pollen Alert")
- `LANGUAGE`: Email language (en-English, de-German)

### 3. Common Email Providers

Here are SMTP settings for some common email providers:

| Provider | SMTP Server | Port | SSL | Auth | Note |
|----------|-------------|------|-----|------|------|
| Gmail | smtp.gmail.com | 587 | false | true | Requires [app password](https://support.google.com/accounts/answer/185833) |
| Outlook | smtp.office365.com | 587 | false | true | |
| Yahoo | smtp.mail.yahoo.com | 587 | false | true | |

### 4. GitHub Actions Configuration

The repository includes a GitHub Actions workflow file (.github/workflows/pollen_scraper.yml) that is set to run automatically at 7:00 AM UTC (8-9 AM Central European Time) every day.

If you want to modify the run time, you can edit the cron expression in that file:

```yaml
on:
  schedule:
    - cron: '0 7 * * *'  # Runs at 7:00 AM UTC every day
```

### 5. Manual Run

You can also trigger the workflow manually through the GitHub Actions page:

1. Go to your forked repository
2. Click the "Actions" tab
3. Select "Pollen Forecast Alert" from the left menu
4. Click the "Run workflow" button

## Advanced Usage

### Command Line Usage

The script can also be run locally, and supports command line arguments:

```bash
# Install dependencies
pip install requests beautifulsoup4

# Basic usage
python pollen_scraper.py --city frankfurt --email-from your.email@example.com --email-to recipient@example.com --email-password yourpassword --smtp-server smtp.example.com --smtp-port 587

# Using built-in email provider configurations
python pollen_scraper.py --city munich --email-from your.email@gmail.com --email-to recipient@example.com --email-password yourpassword --provider gmail

# Switch language
python pollen_scraper.py --city hamburg --language de --provider outlook
```

### Supported Command Line Arguments

```
--city              City name
--email-from        Sender email address
--email-to          Recipient email address
--email-password    Email password or authorization code
--smtp-server       SMTP server address
--smtp-port         SMTP server port
--use-ssl           Use SSL connection
--no-auth           No SMTP authentication required
--sender-name       Sender name
--provider          Email provider (gmail/outlook/yahoo)
--language          Email language (en/de)
```

## Supported Cities

This script supports all German cities with pollen data available on wetteronline.de, including but not limited to:

- berlin
- bonn
- bremen
- cologne (köln)
- dortmund
- dresden
- duesseldorf
- frankfurt
- hamburg
- hannover
- karlsruhe
- leipzig
- munich (münchen)
- nuremberg (nürnberg)
- stuttgart

To find other cities, visit the [pollen page on wetteronline.de](https://www.wetteronline.de/pollen/) and search for your desired city. Then use the city name part of the URL as the `CITY_NAME` parameter.

## Customization and Contribution

Pull Requests or Issues to improve this project are welcome!

Some possible areas for improvement:
- Adding more email templates
- Supporting additional languages
- Adding support for other pollen data sources
- Adding pollen charts and trend analysis
- Implementing multi-city monitoring

## Troubleshooting

If you encounter issues, check the following:

1. Ensure all required GitHub Secrets are correctly set
2. For Gmail, Outlook, and similar services, you may need to use an "app password" instead of your regular password
3. Check the GitHub Actions logs for specific error messages
4. Make sure the city name is spelled correctly and data for that city is available on wetteronline.de

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
