#!/usr/bin/env python3
"""
MAR-PD - Complete All-in-One Runner
Run everything from a single file
"""

import os
import sys
import json
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_complete_extraction():
    """সম্পূর্ণ এক্সট্রাকশন রান করুন"""
    print("""
╔══════════════════════════════════════════════════════╗
║               MAR-PD Complete Runner                 ║
║       All-in-One Account Recovery Solution           ║
╚══════════════════════════════════════════════════════╝
""")
    
    # Import modules dynamically
    from core.extractor import MARPDExtractor
    from methods.method_contacts import ContactExtractor
    from methods.method_backup import BackupDataExtractor
    from methods.method_security import SecurityRecoveryExtractor
    from core.graphql_parser import GraphQLParser
    from core.data_processor import DataProcessor
    
    # Get target
    target = input("\n📥 Enter Facebook Profile URL/Username/UID: ").strip()
    
    if not target:
        print("❌ No input provided.")
        return
    
    print(f"\n🎯 Target: {target}")
    print("⏳ Starting comprehensive extraction...")
    
    try:
        # Initialize all modules
        extractor = MARPDExtractor()
        contact_extractor = ContactExtractor()
        backup_extractor = BackupDataExtractor()
        security_extractor = SecurityRecoveryExtractor()
        graphql_parser = GraphQLParser()
        data_processor = DataProcessor()
        
        # Step 1: Parse target
        print("\n[1/7] Parsing target...")
        uid, username = extractor._parse_target(target)
        
        if not uid and not username:
            print("❌ Could not parse target")
            return
        
        identifier = uid or username
        print(f"✓ Parsed: UID={uid}, Username={username}")
        
        # Step 2: Basic extraction
        print("\n[2/7] Running basic extraction...")
        basic_results = extractor.extract_contacts(target)
        
        # Step 3: Advanced contact extraction
        print("\n[3/7] Running advanced contact extraction...")
        advanced_contacts = contact_extractor.extract_all(uid, username)
        
        # Step 4: Backup data extraction
        print("\n[4/7] Checking backup sources...")
        backup_data = backup_extractor.extract_from_backup_sources(uid, username)
        
        # Step 5: Security info extraction
        print("\n[5/7] Analyzing security information...")
        security_info = security_extractor.extract_security_info(uid, username)
        
        # Step 6: GraphQL analysis
        print("\n[6/7] Querying GraphQL API...")
        graphql_data = graphql_parser.extract_contacts_via_graphql(identifier)
        
        # Step 7: Process and combine all data
        print("\n[7/7] Processing and combining results...")
        
        # Combine all results
        all_results = {
            'target': target,
            'identifier': identifier,
            'timestamp': datetime.now().isoformat(),
            'basic_extraction': basic_results,
            'advanced_contacts': advanced_contacts,
            'backup_data': backup_data,
            'security_info': security_info,
            'graphql_data': graphql_data
        }
        
        # Process through data processor
        processed_results = data_processor.process_contacts({
            'emails': list(set(
                basic_results['contacts']['emails'] +
                advanced_contacts['emails'] +
                backup_data['emails'] +
                list(security_info['recovery_emails']) +
                graphql_data['emails']
            )),
            'phones': list(set(
                basic_results['contacts']['phones'] +
                advanced_contacts['phones'] +
                backup_data['phones'] +
                list(security_info['recovery_phones']) +
                graphql_data['phones']
            )),
            'registration_info': {}
        })
        
        # Add processed results
        all_results['processed_results'] = processed_results
        
        # Save results
        print("\n💾 Saving results...")
        
        # Create results directory
        os.makedirs('results/exports', exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/exports/comprehensive_{timestamp}"
        
        # Save as JSON
        json_file = f"{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        # Create summary report
        txt_file = f"{filename}_summary.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(generate_summary_report(all_results, target))
        
        print(f"\n✅ Extraction complete!")
        print(f"📄 Full data: {json_file}")
        print(f"📋 Summary: {txt_file}")
        
        # Show top recommendations
        show_recommendations(processed_results)
        
    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def generate_summary_report(results, target):
    """সারসংক্ষেপ রিপোর্ট জেনারেট করুন"""
    report = []
    
    report.append("=" * 60)
    report.append("MAR-PD COMPREHENSIVE EXTRACTION REPORT")
    report.append("=" * 60)
    report.append(f"Target: {target}")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Processed results
    processed = results.get('processed_results', {})
    
    # Emails
    if processed.get('emails'):
        report.append("📧 EMAILS FOUND:")
        report.append("-" * 40)
        for email in processed['emails'][:10]:  # Top 10
            if isinstance(email, dict):
                report.append(f"• {email.get('address')} (Score: {email.get('score')}/100)")
            else:
                report.append(f"• {email}")
        report.append("")
    
    # Phones
    if processed.get('phones'):
        report.append("📱 PHONES FOUND:")
        report.append("-" * 40)
        for phone in processed['phones'][:10]:  # Top 10
            if isinstance(phone, dict):
                report.append(f"• {phone.get('formatted')} ({phone.get('operator')}) (Score: {phone.get('score')}/100)")
            else:
                report.append(f"• {phone}")
        report.append("")
    
    # Confidence scores
    if processed.get('confidence_scores'):
        report.append("📊 CONFIDENCE SCORES:")
        report.append("-" * 40)
        for key, value in processed['confidence_scores'].items():
            report.append(f"• {key.replace('_', ' ').title()}: {value}/100")
        report.append("")
    
    # Recommendations
    if processed.get('recommendations'):
        report.append("💡 RECOMMENDATIONS:")
        report.append("-" * 40)
        for rec in processed['recommendations'][:5]:  # Top 5
            report.append(f"• {rec}")
        report.append("")
    
    # Methods used
    report.append("🔧 EXTRACTION METHODS USED:")
    report.append("-" * 40)
    report.append("• Basic Profile Extraction")
    report.append("• Advanced Contact Analysis")
    report.append("• Backup Source Checking")
    report.append("• Security Information Analysis")
    report.append("• GraphQL API Queries")
    report.append("• Intelligent Data Processing")
    report.append("")
    
    # Ethical reminder
    report.append("=" * 60)
    report.append("⚠️  ETHICAL USE REMINDER")
    report.append("=" * 60)
    report.append("This information is for SELF-ACCOUNT RECOVERY ONLY.")
    report.append("Do not use for unauthorized access.")
    report.append("Respect privacy and follow all applicable laws.")
    report.append("=" * 60)
    
    return "\n".join(report)

def show_recommendations(processed_results):
    """রিকমেন্ডেশন দেখান"""
    print("\n" + "=" * 60)
    print("💡 RECOMMENDED ACTION PLAN")
    print("=" * 60)
    
    if processed_results.get('recommendations'):
        for i, rec in enumerate(processed_results['recommendations'][:3], 1):
            print(f"{i}. {rec}")
    
    print("\n🎯 TOP CONTACTS TO TRY:")
    
    # Top emails
    emails = processed_results.get('emails', [])
    if emails:
        print("\n📧 Email (Highest Score):")
        top_email = emails[0] if isinstance(emails[0], dict) else emails[0]
        if isinstance(top_email, dict):
            print(f"   {top_email.get('address')} (Score: {top_email.get('score')}/100)")
        else:
            print(f"   {top_email}")
    
    # Top phones
    phones = processed_results.get('phones', [])
    if phones:
        print("\n📱 Phone (Highest Score):")
        top_phone = phones[0] if isinstance(phones[0], dict) else phones[0]
        if isinstance(top_phone, dict):
            print(f"   {top_phone.get('formatted')} (Score: {top_phone.get('score')}/100)")
        else:
            print(f"   {top_phone}")
    
    print("\n" + "=" * 60)
    print("✅ Use these contacts to recover YOUR account at:")
    print("   https://facebook.com/login/identify")
    print("=" * 60)

if __name__ == "__main__":
    # Check if setup is needed
    if not os.path.exists('requirements.txt'):
        print("First-time setup required...")
        from setup import main as setup_main
        setup_main()
    else:
        run_complete_extraction()