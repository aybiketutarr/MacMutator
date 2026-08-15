        ███╗   ███╗  █████╗   ██████╗   ███╗   ███╗ ██╗   ██╗ ████████╗  █████╗  ████████╗ ██████╗  ██████╗
        ████╗ ████║ ██╔══██╗ ██╔════╝   ████╗ ████║ ██║   ██║ ╚══██╔══╝ ██╔══██╗ ╚══██╔══╝ ██╔══██╗ ██╔══██╗
        ██╔████╔██║ ███████║ ██║        ██╔████╔██║ ██║   ██║    ██║    ███████║    ██║    ██║  ██║ ██████╔╝
        ██║╚██╔╝██║ ██╔══██║ ██║        ██║╚██╔╝██║ ██║   ██║    ██║    ██╔══██║    ██║    ██║  ██║ ██╔══██╗
        ██║ ╚═╝ ██║ ██║  ██║ ╚██████╗   ██║ ╚═╝ ██║ ╚██████╔╝    ██║    ██║  ██║    ██║    ██████╔╝ ██║  ██║
        ╚═╝     ╚═╝ ╚═╝  ╚═╝  ╚═════╝   ╚═╝     ╚═╝  ╚═════╝     ╚═╝    ╚═╝  ╚═╝    ╚═╝    ╚═════╝  ╚═╝  ╚═╝  
                   
                                                    
## purpose 
MacMutator is a lightweight Linux command-line tool for managing MAC addresses on network interfaces. It allows users to generate a random locally administered MAC address, view the current MAC address, and restore the original address when needed.
The tool is designed to keep MAC address operations simple and practical, while providing useful safeguards such as saving the original address and verifying changes after each operation.
MacMutator can be used for cybersecurity labs, network testing, virtual machine environments, CTFs, and other authorized security and networking activities.

**Who Can Use MacMutator?**
It can be useful for:

-  **Cybersecurity students** — for learning network concepts and practicing MAC address manipulation in controlled lab environments.
-  **Penetration testers** — for authorized security assessments where MAC address changes are part of the testing process.
-  **Network security professionals** — for testing MAC-based access controls and network configurations.
-  **CTF participants** — for cybersecurity challenges and isolated practice environments.
-  **Linux users and system administrators** — for network interface testing and configuration.
-  **Virtualization and lab users** — for experimenting with network interfaces in virtual machines and isolated environments.

MacMutator is intended for educational, testing, and authorized security purposes. It should only be used on systems and networks where you have permission to modify the network configuration.

---

![OVERVİEW](Overview.png)

## features

- Random MAC address generation and usage
- MAC address restoration
- Displaying the current MAC address
- Automatic backup of the original MAC address
- MAC address validation
- Network interface support
- Command-line argument support (--help, --random, --show, --restore)
- Root privilege and system requirement checks
- Progress indicators and terminal status output
- Error handling and validation
- System-wide installation support

 ---


 ## 📦 Installation and usage
 
 ```bash
git clone https://github.com/aybiketutarr/MacMutator.git
cd MacMutator
chmod +x install.sh
sudo ./install.sh
```

> *Note: The installer will configure MacMutator for system-wide use.*

Check the installed version:
```bash
macmutator --version
```
You can also check the available commands:
```bash
macmutator --help
```

If the command returns the MacMutator version or help menu, the installation was successful.

> **Warning:** Root privileges are required for operations that modify or restore a MAC address. Only use MacMutator on systems and network interfaces that you own or have explicit permission to modify.




