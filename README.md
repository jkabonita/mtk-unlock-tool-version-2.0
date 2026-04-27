<div align="center">

# MTKClient

![Logo](mtkclient/gui/images/logo_256.png)

**Reverse Engineering & Flash Tool for MediaTek Devices**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv3-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/bkerler/mtkclient)

A powerful tool for MediaTek device exploitation, flash reading/writing, and advanced operations.

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-cli-reference) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
  - [Quick Start - Live DVD](#-quick-start---live-dvd)
  - [Linux / macOS](#-linux--macos)
  - [Windows](#-windows)
  - [Kamakiri Setup](#-kamakiri-setup-optional)
- [Usage](#-usage)
  - [GUI Mode](#-gui-mode)
  - [Common Operations](#-common-operations)
- [CLI Reference](#-cli-reference)
- [Troubleshooting](#-troubleshooting)
- [Credits](#-credits)
- [License](#-license)

---

## 🔍 Overview

MTKClient is a comprehensive toolkit for MediaTek-based devices, enabling flash memory operations, bootloader unlocking, partition management, and advanced security operations.

### Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| **Windows** | ✅ Full Support | Requires UsbDk driver |
| **Linux** | ✅ Full Support | Kernel patch needed for old kamakiri only |
| **macOS** | ✅ Full Support | Native support |

### Device Boot Mode

To use MTKClient:
1. Power off your device
2. Press and hold **Vol Up + Power** or **Vol Down + Power**
3. Connect USB cable
4. Release buttons when detected

---

## ✨ Features

### Core Capabilities
- 📱 **Flash Operations**: Read, write, and erase partitions
- 🔓 **Bootloader Unlock**: Unlock/lock bootloader
- 🔑 **Key Extraction**: Extract RPMB, FDE, and encryption keys
- 💾 **Full Dumps**: Complete flash dumps and partition backups
- 🛠️ **Memory Access**: Direct memory read/write operations
- 🚀 **Payload Execution**: Run custom payloads (kamakiri, amonet, hashimoto)

### Advanced Features
- GPT table manipulation
- BROM/Preloader/SRAM dumping
- RPMB operations
- Security configuration (seccfg)
- eFuse reading
- Stage2 payload support
- Meta mode activation

---

## 📦 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **USB**: Working USB port
- **Drivers**: Platform-specific (see installation)

### Python Dependencies
```
pyusb >= 1.2.1
pycryptodome >= 3.15.0
colorama >= 0.4.4
pyserial >= 3.5
PySide6 >= 6.4.0.1 (for GUI)
```

---

## 🚀 Installation

### 💿 Quick Start - Live DVD

For the easiest setup, use the pre-configured Live DVD (Ubuntu 22.04 LTS):

| Download | Credentials |
|----------|-------------|
| [Live DVD V4](https://www.androidfilehost.com/?fid=15664248565197184488) | User: `user` |
| [Mirror](https://drive.google.com/file/d/10OEw1d-Ul_96MuT3WxQ3iAHoPC4NhM_X/view?usp=sharing) | Password: `user` |

---

### 🐧 Linux / macOS

**Ubuntu/Debian recommended. No patched kernel needed except for old kamakiri.**

#### 1. Install Dependencies

```bash
sudo apt install python3 git libusb-1.0-0 python3-pip
```

#### 2. Clone and Install

```bash
git clone https://github.com/bkerler/mtkclient
cd mtkclient
pip3 install -r requirements.txt
python3 setup.py build
python3 setup.py install
```

#### 3. Configure USB Permissions

```bash
# Add user to required groups
sudo usermod -a -G plugdev $USER
sudo usermod -a -G dialout $USER

# Install udev rules
sudo cp Setup/Linux/*.rules /etc/udev/rules.d
sudo udevadm control -R
```

> **⚠️ Important**: Reboot after adding user to groups!

#### 4. Special Cases

For devices with vendor interface 0xFF (e.g., LG):
```bash
echo "blacklist qcaux" | sudo tee -a /etc/modprobe.d/blacklist.conf
```

---

### 🪟 Windows

#### 1. Install Python and Git

- Download and install [Python 3.9+](https://www.python.org/downloads/)
- Download and install [Git](https://git-scm.com/download/win)

> **⚠️ Note**: If installing Python from Microsoft Store, skip `python setup.py install` step.

#### 2. Clone and Install

Open Command Prompt (`WIN+R` → `cmd`):

```cmd
git clone https://github.com/bkerler/mtkclient
cd mtkclient
pip3 install -r requirements.txt
```

#### 3. Install UsbDk Driver

1. Install MTK Serial Port driver (or use Windows default COM Port driver)
2. Download [UsbDk installer (.msi)](https://github.com/daynix/UsbDk/releases/)
3. Install UsbDk
4. Verify installation:
   ```cmd
   UsbDkController -n
   ```
   Look for device with VID `0x0E8D` and PID `0x0003`

> ✅ **Tested on Windows 10 and 11**

---

### 🔧 Kamakiri Setup (Optional)

**Only required for MT6260 or older chipsets.**

<details>
<summary>Click to expand kernel patching instructions</summary>

#### Install Build Dependencies

```bash
sudo apt-get install build-essential libncurses-dev bison flex libssl-dev libelf-dev libdw-dev
git clone https://git.kernel.org/pub/scm/devel/pahole/pahole.git
cd pahole && mkdir build && cd build && cmake .. && make && sudo make install
sudo mv /usr/local/libdwarves* /usr/local/lib/ && sudo ldconfig
```

#### Patch and Build Kernel

```bash
wget https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-`uname -r`.tar.xz
tar xvf linux-`uname -r`.tar.xz
cd linux-`uname -r`
patch -p1 < ../Setup/kernelpatches/disable-usb-checks-5.10.patch
cp -v /boot/config-$(uname -r) .config
make menuconfig
make
sudo make modules_install 
sudo make install
sudo reboot
```

> 💡 **Tip**: Check `Setup/kernels` for pre-built kernel configurations.

</details>

---

## 📖 Usage

### 🖥️ GUI Mode

Launch the graphical interface for basic operations:

```bash
python mtk_gui
```

**GUI Features:**
- ✅ Partition dumping
- ✅ Full flash backup
- ✅ Flash writing
- ✅ Bootloader unlock/lock
- ✅ Key generation
- ✅ Progress tracking

---

### 💻 Script Mode

Run multiple commands from a script file:

```bash
python mtk script run.example
```

See `run.example` for script structure.

---

## 🔓 Common Operations

### Root Your Device

**Tested on Android 9-12**

#### Step 1: Dump Boot Partitions

```bash
python mtk r boot,vbmeta boot.img,vbmeta.img
python mtk reset
```

#### Step 2: Install Magisk

1. Download [Magisk for MTK](https://raw.githubusercontent.com/vvb2060/magisk_files/44ca9ed38c29e22fa276698f6c03bc1168df2c10/app-release.apk)

2. Enable Developer Options:
   - Go to **Settings → About Phone → Build Number**
   - Tap 7 times to enable Developer Options
   - Enable **OEM Unlock** and **USB Debugging**

3. Install Magisk:
   ```bash
   adb install app-release.apk
   ```
   > Accept the RSA authentication prompt on your device

#### Step 3: Patch Boot Image

```bash
# Upload boot image
adb push boot.img /sdcard/Download

# Patch using Magisk app (tap Install → Select boot.img)

# Download patched boot
adb pull /sdcard/Download/magisk_patched_[xxxxx].img
mv magisk_patched_[xxxxx].img boot.patched
```

#### Step 4: Unlock Bootloader

See [Unlock Bootloader](#unlock-bootloader) section below.

#### Step 5: Flash Patched Boot

```bash
python mtk w boot,vbmeta boot.patched,vbmeta.img.empty
python mtk reset
```

#### Step 6: Enjoy! 🎉

Disconnect USB and reboot. Your device is now rooted!

---

### 🔓 Unlock Bootloader

#### Step 1: Erase Metadata

```bash
python mtk e metadata,userdata,md_udc
```

#### Step 2: Unlock

```bash
python mtk da seccfg unlock
```

To relock:
```bash
python mtk da seccfg lock
```

#### Step 3: Reboot

```bash
python mtk reset
```

Disconnect USB cable to complete reboot.

> **⚠️ Android 11 Note**: If you see a dm-verity error, press the power button. The device will show a yellow warning about unlocked bootloader and boot within 5 seconds.

---

## � CLI Reference

### Flash Operations

#### Read Flash

```bash
# Read partition
python mtk r boot boot.bin

# Read partition via bootrom
python mtk r boot boot.bin --preloader=Loader/Preloader/your_device_preloader.bin

# Read preloader partition
python mtk r preloader preloader.bin --parttype=boot1

# Read full flash
python mtk rf flash.bin

# Read flash offset
python mtk ro 0x128000 0x200000 flash.bin

# Dump all partitions
python mtk rl out

# Show GPT
python mtk printgpt
```

#### Write Flash

```bash
# Write partition
python mtk w boot boot.bin

# Write full flash (DA mode only)
python mtk wf flash.bin

# Write all partitions from directory
python mtk wl out

# Write to flash offset
python mtk wo 0x128000 0x200000 flash.bin
```

#### Erase Flash

```bash
# Erase partition
python mtk e boot

# Erase sectors
python mtk es boot [sector count]

# Erase specific sectors
python mtk ess [start sector] [sector count]
```

---

### DA Commands

```bash
# Peek memory
python mtk da peek [addr] [length] --filename output.bin

# Poke memory
python mtk da poke [addr] [data]

# Read RPMB
python mtk da rpmb r --filename rpmb.bin

# Write RPMB
python mtk da rpmb w filename

# Generate keys
python mtk da generatekeys

# Read eFuses
python mtk da efuse

# Unlock/Lock bootloader
python mtk da seccfg unlock
python mtk da seccfg lock
```

---

### Advanced Operations

```bash
# Bypass SLA, DAA, SBC
python mtk payload

# Boot to meta mode
python mtk payload --metamode FASTBOOT

# Dump preloader
python mtk dumppreloader --ptype=kamakiri --filename=preloader.bin

# Dump BROM
python mtk dumpbrom --ptype=kamakiri --filename=brom.bin

# Dump SRAM
python mtk dumpsram --filename=sram.bin

# Brute force bootrom
python mtk brute

# Crash DA to enter BROM
python mtk crash

# Read memory with patched preloader
python mtk peek [addr] [length] --preloader=patched_preloader.bin

# Run custom payload
python mtk payload --payload=payload.bin
```

---

### Stage2 Operations

```bash
# Run stage2 in bootrom
python mtk stage

# Run stage2 in preloader
python mtk plstage

# Run stage2 with preloader
python mtk plstage --preloader=preloader.bin
```

#### Stage2 Commands

```bash
# Reboot
python stage2 reboot

# Read RPMB
python stage2 rpmb

# Read preloader
python stage2 preloader

# Read memory
python stage2 memread [addr] [length]
python stage2 memread [addr] [length] --filename output.bin

# Write memory
python stage2 memwrite [addr] --data [hexstring]
python stage2 memwrite [addr] --filename input.bin

# Extract keys
python stage2 keys --mode sej
python stage2 keys --mode dxcc  # Use plstage for dxcc

# Generate seccfg
python stage2 seccfg unlock
python stage2 seccfg lock
```

---

## 🐛 Troubleshooting

### Enable Debug Mode

Run any command with `--debugmode` to generate detailed logs:

```bash
python mtk [command] --debugmode
```

Log will be written to `log.txt`.

### Common Issues

| Issue | Solution |
|-------|----------|
| Device not detected | Check USB cable, try different port, verify drivers |
| Permission denied (Linux) | Add user to `plugdev` and `dialout` groups, reboot |
| UsbDk not working (Windows) | Reinstall UsbDk, check device manager |
| Connection timeout | Try different USB port, restart device in BROM mode |

### Configuration

- **Chip configs**: `config/brom_config.py`
- **USB IDs**: `config/usb_ids.py`

---

## 👥 Credits

- **kamakiri** - [xyzz]
- **linecode exploit** - [chimera]
- **Chaosmaster**
- **Geert-Jan Kreileman** - GUI, design & fixes
- **jkabonita**
- **All contributors**

---

## 📄 License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Use at your own risk. The authors are not responsible for any damage caused by misuse of this tool.

---

<div align="center">

**Made with ❤️ by the MTKClient community**

[Report Bug](https://github.com/bkerler/mtkclient/issues) • [Request Feature](https://github.com/bkerler/mtkclient/issues)

</div>
