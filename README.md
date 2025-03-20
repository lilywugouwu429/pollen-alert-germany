# Pollen Forecast Email Alert

![Pollen Alert](https://img.shields.io/badge/Pollen-Alert-green)
![Language](https://img.shields.io/badge/Language-Python-blue)
![License](https://img.shields.io/badge/License-MIT-orange)

This project uses GitHub Actions to automatically scrape pollen concentration data from [wetteronline.de](https://www.wetteronline.de/pollen/) and send daily email notifications. Perfect for people with pollen allergies who want to monitor local pollen levels.

🔗 **[Live Demo](https://yliu.tech//pollen-alert-germany/)**

## Features

- 🌱 Automatically fetches pollen forecast data for specified cities
- 📊 Displays concentration levels for different pollen types in an intuitive format
- 📧 Supports multiple email service providers (Gmail, Outlook, Yahoo)
- 🌐 Multi-language support (English, German, and Chinese)
- 🔄 Configurable for daily automatic updates
- 📱 Beautiful HTML email format, mobile-friendly
- 🔧 Highly customizable with command-line arguments and environment variables

## Setup Guide

### 1. Fork this repository

First, click the "Fork" button in the top right corner of this repository to create a copy in your GitHub account.

### 2. Enable GitHub Actions workflow

⚠️ **IMPORTANT**: The workflow is disabled by default. After forking, you need to enable it:

1. Go to your forked repository
2. Click the "Actions" tab
3. Click the "I understand my workflows, go ahead and enable them" button
4. Find the "Pollen Forecast Alert" workflow
5. Click the "Enable workflow" button

### 3. Configure GitHub Secrets

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
- `LANGUAGE`: Email language (en-English, de-German, zh-Chinese)

### 4. Common Email Providers

Here are SMTP settings for some common email providers:

| Provider | SMTP Server | Port | SSL | Auth | Note |
|----------|-------------|------|-----|------|------|
| Gmail | smtp.gmail.com | 587 | false | true | Requires [app password](https://support.google.com/accounts/answer/185833) |
| Outlook | smtp.office365.com | 587 | false | true | |
| Yahoo | smtp.mail.yahoo.com | 587 | false | true | |

### 5. GitHub Actions Configuration

The repository includes a GitHub Actions workflow file (.github/workflows/pollen_scraper.yml) that is set to run automatically at 7:00 AM UTC (8-9 AM Central European Time) every day once enabled.

If you want to modify the run time, you can edit the cron expression in that file:

```yaml
on:
  schedule:
    - cron: '0 7 * * *'  # Runs at 7:00 AM UTC every day
```

### 6. Manual Run

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
pip install -r requirements.txt

# Basic usage
python pollen_scraper.py --city frankfurt --email-from your.email@example.com --email-to recipient@example.com --email-password yourpassword --smtp-server smtp.example.com --smtp-port 587

# Using built-in email provider configurations
python pollen_scraper.py --city munich --email-from your.email@gmail.com --email-to recipient@example.com --email-password yourpassword --provider gmail

# Switch language
python pollen_scraper.py --city hamburg --language de --provider outlook

# Use Chinese language
python pollen_scraper.py --city berlin --language zh --provider gmail
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
--language          Email language (en/de/zh)
```

## Multi-Language Support

The script supports three languages for email notifications:

1. **English (en)** - Default language with English pollen names
2. **German (de)** - German email interface with English pollen name translations
3. **Chinese (zh)** - Chinese email interface with Chinese pollen name translations

Each language version includes:
- Localized interface text
- Translated pollen type names
- Appropriate concentration level indicators

You can select the language by setting the `LANGUAGE` environment variable or using the `--language` command line argument.

## Supported Cities

This script supports all German cities with pollen data available on wetteronline.de, including but not limited to:

- berlin
- bonn
- bremen
- koeln (for Köln/Cologne)
- dortmund
- dresden
- duesseldorf (for Düsseldorf)
- frankfurt
- hamburg
- hannover
- karlsruhe
- leipzig
- muenchen (for München/Munich)
- nuernberg (for Nürnberg/Nuremberg)
- stuttgart

**Important Note**: When entering city names that contain umlauts (ä, ö, ü), you must convert them to their equivalent form:
- ä → ae (München → muenchen)
- ö → oe (Köln → koeln)
- ü → ue (Düsseldorf → duesseldorf)

To find other cities, visit the [pollen page on wetteronline.de](https://www.wetteronline.de/pollen/) and search for your desired city. Then use the city name part of the URL as the `CITY_NAME` parameter.

## Pollen Types and Translations

The script provides translations for common pollen types in German, English, and Chinese:

| German (Original) | English | Chinese |
|-------------------|---------|---------|
| Ambrosia | Ragweed | 豚草 |
| Ampfer | Sorrel | 酸模 |
| Beifuß | Mugwort | 艾蒿 |
| Birke | Birch | 桦树 |
| Buche | Beech | 山毛榉 |
| Erle | Alder | 桤木 |
| Esche | Ash | 梣树 |
| Gräser | Grasses | 草 |
| Hasel | Hazel | 榛树 |
| Pappel | Poplar | 杨树 |
| Roggen | Rye | 黑麦 |
| Ulme | Elm | 榆树 |
| Wegerich | Plantain | 车前草 |
| Weide | Willow | 柳树 |

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
5. Verify that you've enabled the GitHub Actions workflow after forking

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
