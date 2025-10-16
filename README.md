# Restaurant Access Control System

A facial recognition-based access control system for school restaurants that verifies student identity and manages account balances.

## 🎯 Project Overview

This application allows restaurants to control access through facial recognition technology. Students are identified by their photos, and access is granted based on their account balance.

### Key Features

- **Facial Recognition**: Identify students using computer vision
- **Balance Management**: Track and manage student account balances
- **Admin Interface**: Secure admin panel for student management
- **Dual Access Modes**: Camera-based or file upload identification
- **Real-time Processing**: Live camera feed with instant recognition

## 🚀 Installation & Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam (optional, for live recognition)
- Windows/macOS/Linux compatible

### Quick Start (Recommended)

**Windows Users:**
```bash
# Double-click start.bat or run in PowerShell:
.\start.bat
```

**All Platforms:**
```bash
# Option 1: Demo version (works immediately)
python demo.py

# Option 2: Full version with authentication
python main.py

# Option 3: Interactive launcher
python launcher.py
```

### Full Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/PythonTP.git
   cd PythonTP
   ```

2. **Install dependencies (optional for demo)**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py  # Full version
   # OR
   python demo.py  # Demo version (no dependencies needed)
   ```

### Troubleshooting Installation

If you encounter issues with `dlib` or `face_recognition`:

**Windows:**
```bash
# Install Visual Studio Build Tools first
pip install cmake
pip install dlib
pip install face-recognition
```

**macOS:**
```bash
brew install cmake
pip install dlib
pip install face-recognition
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install cmake
sudo apt-get install libopenblas-dev liblapack-dev
pip install dlib
pip install face-recognition
```

## 🏗️ Project Structure

```
PythonTP/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── main.py                     # Application entry point
├── gui.py                      # GUI interface (Tkinter)
├── face_recognition_utils.py   # Facial recognition utilities
├── db.py                       # Database management (JSON)
├── students.json               # Student database (auto-created)
├── images/                     # Student photos directory
│   └── (student photos)
├── tests/
│   └── test_scenarios.md       # Test scenarios
└── docs/
    ├── rapport.md              # Technical report
    └── screenshots/            # Application screenshots
```

## 🎮 Usage

### Starting the Application

1. **Run the main application**
   ```bash
   python main.py
   ```

2. **Admin Authentication**
   - Default credentials are provided in the login dialog
   - Use: `admin` / `restaurant123`

3. **Choose Operation Mode**
   - **Access Control**: For student identification and restaurant access
   - **Student Management**: For adding students and managing balances

### Access Control Mode

1. **Camera Access**
   - Click "Start Camera" to begin live feed
   - Click "Capture & Identify" to identify current person
   - System will automatically grant/deny access based on balance

2. **File Upload**
   - Click "Select Image File" to upload a photo
   - System will identify the student and process access

### Student Management Mode

#### Adding Students

1. Switch to "Student Management" mode
2. Go to "Add Student" tab
3. Fill in student information:
   - Student ID (unique identifier)
   - First Name
   - Last Name
   - Initial Balance (default: €50.00)
4. Select student photo (must contain exactly one face)
5. Click "Add Student"

#### Managing Balances

1. Go to "Manage Balance" tab
2. Enter Student ID
3. Use "Add Balance" to top up account
4. Use "Check Balance" to view current balance

#### Viewing Students

1. Go to "View Students" tab
2. See all registered students with their information
3. Use "Refresh List" to update the display
4. Use "Reload Face Database" to update recognition system

## 🔧 Configuration

### Admin Credentials

Default admin accounts (can be modified in `main.py`):
- `admin` / `restaurant123`
- `manager` / `access456`
- `supervisor` / `control789`

### System Parameters

You can modify these parameters in the respective files:

**Face Recognition (face_recognition_utils.py):**
- `tolerance = 0.6` - Recognition sensitivity (lower = more strict)
- Image requirements: minimum 100x100 pixels, single face

**Database (db.py):**
- Default balance: €50.00 per student
- Meal cost: €4.00 per access

## 🧪 Testing

### Test Scenarios

1. **Student Registration**
   - Add new student with valid photo
   - Verify student appears in database
   - Check face encoding is created

2. **Access Control**
   - Test with registered student (sufficient balance)
   - Test with registered student (insufficient balance)
   - Test with unregistered person
   - Test with invalid photo

3. **Balance Management**
   - Add balance to student account
   - Verify balance deduction after access
   - Check balance history

### Sample Test Data

The system includes realistic test scenarios:
- Student names and IDs
- Realistic balance amounts
- Various test cases for edge conditions

## 🛠️ Technical Details

### Dependencies

- **face_recognition**: Primary facial recognition library
- **opencv-python**: Computer vision and camera handling
- **dlib**: Face detection and landmark recognition
- **numpy**: Numerical computations
- **Pillow**: Image processing
- **tkinter**: GUI framework (included with Python)

### Architecture

1. **Database Layer (db.py)**: JSON-based student data storage
2. **Recognition Layer (face_recognition_utils.py)**: Face encoding and matching
3. **Interface Layer (gui.py)**: Tkinter-based user interface
4. **Application Layer (main.py)**: Authentication and application orchestration

### Data Flow

1. Student photo → Face encoding → Database storage
2. Live camera/uploaded image → Face detection → Face encoding
3. Encoding comparison → Student identification → Balance check
4. Access decision → Balance deduction → Result display

## 🎯 Features Status

### ✅ Implemented Features

- [x] Student registration with photo
- [x] Facial recognition identification
- [x] Balance management system
- [x] Admin authentication
- [x] Camera-based access control
- [x] File upload identification
- [x] Real-time camera feed
- [x] Student database management
- [x] Balance deduction for meals
- [x] Access logging and statistics

### 🚧 Optional Features (Future Enhancements)

- [ ] Encrypted password storage
- [ ] Network-based database
- [ ] Multiple camera support
- [ ] Advanced reporting system
- [ ] Email notifications
- [ ] Mobile app integration

## 🔍 Troubleshooting

### Common Issues

**"No face detected"**
- Ensure good lighting
- Make sure face is clearly visible
- Check camera permissions

**"Import errors"**
- Verify all dependencies are installed
- Check Python version compatibility
- Try reinstalling packages

**"Camera not opening"**
- Check camera permissions
- Ensure camera is not used by another application
- Try different camera index in code

**"Low recognition accuracy"**
- Use high-quality photos
- Ensure consistent lighting
- Consider adjusting tolerance parameter

## 📊 Performance Notes

- Face recognition processing: ~1-3 seconds per image
- Camera feed: 30 FPS capability
- Database operations: Instant for small datasets (<1000 students)
- Memory usage: ~50-100MB typical

## 🤝 Contributing

This is an educational project. When submitting improvements:

1. Document your changes clearly
2. Test thoroughly with various scenarios
3. Maintain code comments and documentation
4. Follow existing code style

## 📄 License

This project is created for educational purposes as part of a Python development course.

## 📞 Support

For technical issues or questions:
- Check the troubleshooting section
- Review the test scenarios
- Consult the technical documentation in `docs/rapport.md`

---

**⚠️ Security Note**: This system is designed for educational purposes. In production environments, implement proper security measures including encrypted password storage, secure network protocols, and regular security audits.