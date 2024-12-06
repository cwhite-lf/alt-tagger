# WordPress Image Alt Text Generator

A Python script that automatically generates alt text for WordPress media library images using OpenAI's Vision API.

## Features

- Connects to WordPress REST API to fetch media items
- Identifies images missing alt text
- Generates descriptive alt text using OpenAI's Vision API
- Supports dry-run and update modes
- Exports results to CSV
- Configurable image processing limits

## Prerequisites

- Python 3.8+
- WordPress site with REST API enabled
- OpenAI API key

## Installation

1. Clone the repository: 

```
git clone https://github.com/yourusername/wordpress-alt-text-generator.git
cd wordpress-alt-text-generator
```

2. Install dependencies using pipenv:
`pipenv install`

3. Create a `.env` file in the project root:

`API_KEY_OPENAI=your_openai_api_key_here`

## Usage

Basic usage:

`python tagger.py <wordpress_url> [model] [mode] [limit]`

Arguments:
    -m, --model  : OpenAI model to use (default: gpt-4o-mini)
    -w, --write  : Enable write mode (default: dry-run if omitted)
    -l, --limit  : Number of images to process (default: 10, 0 for all)
    -o, --output : Output CSV file (default: domain_name.csv)

Example:
`python tagger.py https://lafleur.marketing gpt-4 update 20`


## Output

The script generates a CSV file (`image_alt_text_results.csv`) containing:
- Image ID
- Title
- Original alt text (if any)
- Generated alt text
- Image URL

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.