# Gym-Bot Modular

A comprehensive, modular gym management bot for ClubHub integration with automated token extraction, payment processing, and member communication.

## 🚀 Features

- **Automated Token Extraction**: Smart Charles Proxy integration for seamless ClubHub authentication
- **Payment Processing**: Square integration for overdue payment handling
- **Member Communication**: Automated messaging and notifications
- **Modular Architecture**: Clean, maintainable codebase with separation of concerns
- **AI Integration**: Gemini AI for intelligent conversation handling
- **Calendar Integration**: Automated scheduling and appointment management

## 📁 Project Structure

```
gym-bot-modular/
├── config/                 # Configuration files
│   ├── constants.py        # Application constants
│   └── secrets.py          # Secret management
├── core/                   # Core functionality
│   ├── authentication.py   # Authentication handling
│   └── driver.py          # Web driver management
├── services/              # Service layer
│   ├── ai/               # AI services (Gemini)
│   ├── api/              # API clients (ClubHub, Square)
│   ├── authentication/    # Token extraction and management
│   ├── calendar/         # Calendar integration
│   ├── clubos/           # ClubOS messaging
│   ├── data/             # Data management
│   ├── notifications/    # Multi-channel notifications
│   └── payments/         # Payment processing
├── utils/                # Utility functions
├── workflows/            # Business logic workflows
├── web/                  # Web interface (if applicable)
├── smart_token_capture.py # Automated token extraction
└── main.py              # Application entry point
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gym-bot-modular
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure secrets**
   - Copy `config/secrets.py.example` to `config/secrets.py`
   - Fill in your API keys and credentials

4. **Set up Charles Proxy** (for token extraction)
   - Install Charles Proxy
   - Configure it to capture ClubHub traffic
   - Run `smart_token_capture.py` to extract tokens

## 🔧 Usage

### Token Extraction
```bash
python smart_token_capture.py
```

### Main Bot
```bash
python main.py
```

### Individual Workflows
```bash
python -m gym_bot.workflows.overdue_payments_optimized
python -m gym_bot.workflows.member_messaging
```

## 🔐 Authentication

The bot uses automated token extraction from Charles Proxy sessions:

1. **Start Charles Proxy**
2. **Use ClubHub app** on your device
3. **Run token capture** - automatically extracts and stores tokens
4. **Use tokens** - bot automatically uses fresh tokens for API calls

## 📊 Features

### Payment Processing
- Automated overdue payment detection
- Square integration for payment processing
- Invoice generation and tracking

### Member Communication
- Automated messaging workflows
- Multi-channel notifications
- Intelligent conversation handling

### Data Management
- Member data synchronization
- CSV import/export
- Advanced data analytics

## 🤖 AI Integration

Powered by Google Gemini AI for:
- Intelligent conversation handling
- Automated response generation
- Context-aware interactions

## 🔄 Workflows

### Overdue Payments
- Detects overdue payments
- Generates invoices
- Sends payment reminders
- Processes payments via Square

### Member Messaging
- Automated welcome messages
- Payment reminders
- Event notifications
- Custom messaging campaigns

## 📝 Configuration

Key configuration files:
- `config/constants.py` - Application settings
- `config/secrets.py` - API keys and credentials
- `gym_bot/services/authentication/clubhub_token_capture.py` - Token extraction

## 🧪 Testing

```bash
# Run token extraction test
python smart_token_capture.py

# Test API connections
python -m gym_bot.services.api.clubos_api_client

# Test payment processing
python -m gym_bot.services.payments.square_client
```

## 📈 Monitoring

- Logs stored in `logs/` directory
- Token extraction logs
- API call monitoring
- Error tracking and reporting

## 🔧 Development

### Adding New Services
1. Create new module in `services/`
2. Implement interface
3. Add to main workflow
4. Update documentation

### Adding New Workflows
1. Create workflow in `workflows/`
2. Implement business logic
3. Add configuration
4. Test thoroughly

## 📄 License

[Add your license here]

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📞 Support

For issues and questions:
- Check logs in `logs/` directory
- Review configuration files
- Test token extraction process
- Verify API credentials

---

**Built with ❤️ for gym management automation**
