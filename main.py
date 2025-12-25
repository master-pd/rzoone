#!/usr/bin/env python3
"""
MAR-PD - Main Entry Point
Author: Master
100% Working Contact Extractor
"""

import sys
import os
from core.extractor import MARPDExtractor
from utils.logger import setup_logger
from utils.validator import validate_input
from colorama import init, Fore, Style

init(autoreset=True)

def show_banner():
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                    {Fore.YELLOW}MAR-PD v3.5{Fore.CYAN}                              ║
║           {Fore.GREEN}Multi-Algorithmic Reconnaissance - Profile Decoder{Fore.CYAN}    ║
║                    {Fore.MAGENTA}Contact Extractor Module{Fore.CYAN}                    ║
╚══════════════════════════════════════════════════════════════╝
{Fore.RESET}
"""
    print(banner)

def main():
    show_banner()
    
    # Setup logger
    logger = setup_logger()
    
    # Initialize extractor
    extractor = MARPDExtractor()
    
    # Get input
    print(f"\n{Fore.YELLOW}[+] Enter Facebook Profile URL or UID:")
    print(f"{Fore.CYAN}Examples:")
    print(f"  • https://facebook.com/username")
    print(f"  • https://facebook.com/profile.php?id=1000XXXXXXX")
    print(f"  • username (without URL)")
    print(f"  • 1000XXXXXXX (numeric UID){Fore.RESET}")
    
    target = input(f"\n{Fore.GREEN}[?] Input: {Fore.RESET}").strip()
    
    if not target:
        print(f"{Fore.RED}[!] No input provided. Exiting.{Fore.RESET}")
        sys.exit(1)
    
    # Validate input
    if not validate_input(target):
        print(f"{Fore.RED}[!] Invalid input format.{Fore.RESET}")
        sys.exit(1)
    
    print(f"\n{Fore.YELLOW}[*] Starting extraction for: {target}{Fore.RESET}")
    print(f"{Fore.CYAN}[*] This may take 2-5 minutes...{Fore.RESET}\n")
    
    try:
        # Start extraction
        results = extractor.extract_contacts(target)
        
        # Display results
        print(f"\n{Fore.GREEN}{'='*60}{Fore.RESET}")
        print(f"{Fore.GREEN}[✓] EXTRACTION COMPLETED{Fore.RESET}")
        print(f"{Fore.GREEN}{'='*60}{Fore.RESET}")
        
        if results.get('success'):
            contacts = results.get('contacts', {})
            
            print(f"\n{Fore.YELLOW}[+] FOUND CONTACTS:{Fore.RESET}")
            print(f"{Fore.CYAN}{'-'*40}{Fore.RESET}")
            
            if contacts.get('emails'):
                print(f"\n{Fore.GREEN}📧 Email Addresses:{Fore.RESET}")
                for email in contacts['emails']:
                    print(f"  • {email}")
            
            if contacts.get('phones'):
                print(f"\n{Fore.GREEN}📱 Phone Numbers:{Fore.RESET}")
                for phone in contacts['phones']:
                    print(f"  • {phone}")
            
            if contacts.get('registration_info'):
                reg_info = contacts['registration_info']
                print(f"\n{Fore.GREEN}📝 Registration Info:{Fore.RESET}")
                for key, value in reg_info.items():
                    if value:
                        print(f"  • {key}: {value}")
            
            # Save results
            output_file = extractor.save_results(results, target)
            print(f"\n{Fore.GREEN}[+] Results saved to: {output_file}{Fore.RESET}")
            
        else:
            print(f"\n{Fore.RED}[!] No contacts found.{Fore.RESET}")
            print(f"{Fore.YELLOW}[*] Try these alternative methods:{Fore.RESET}")
            print(f"  1. Use Facebook's official recovery")
            print(f"  2. Check backup email/phone in settings")
            print(f"  3. Contact Facebook support")
        
        print(f"\n{Fore.CYAN}{'='*60}{Fore.RESET}")
        print(f"{Fore.CYAN}[*] Tool execution completed.{Fore.RESET}")
        print(f"{Fore.CYAN}[*] Use results responsibly for account recovery only.{Fore.RESET}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Process interrupted by user.{Fore.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {str(e)}{Fore.RESET}")
        logger.error(f"Extraction failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()