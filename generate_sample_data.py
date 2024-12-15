# generate_sample_data.py
import random
import argparse
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom
import names
import faker


def generate_phone():
    """Generate a random US phone number"""
    return f"+1{random.randint(2000000000, 9999999999)}"


def generate_message():
    """Generate a random message"""
    fake = faker.Faker()
    templates = [
        lambda: fake.sentence(),
        lambda: fake.text(max_nb_chars=100),
        lambda: "👋 " + fake.sentence(),
        lambda: "Can you " + fake.sentence().lower(),
        lambda: "Hey! " + fake.sentence(),
        lambda: fake.sentence() + " 😊",
        lambda: "Yes" if random.random() < 0.5 else "No",
        lambda: (
            fake.sentence() + "?" if random.random() < 0.3 else fake.sentence()
        ),
    ]
    return random.choice(templates)()


def create_sample_backup(
    num_messages=1000, num_contacts=10, start_date=None, end_date=None
):
    """Create a sample SMS backup XML file"""
    # Set up dates
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=365)

    # Generate contacts
    contacts = []
    for _ in range(num_contacts):
        contacts.append(
            {
                "name": names.get_full_name(),
                "phone": generate_phone(),
                "message_prob": random.uniform(
                    0.05, 0.3
                ),  # Different conversation frequencies
            }
        )

    # Create XML structure
    root = ET.Element("smses")
    root.set("count", str(num_messages))
    root.set("backup_set", "sample_data")
    root.set("backup_date", str(int(datetime.now().timestamp() * 1000)))
    root.set("type", "full")

    # Add header comment
    header = ET.Comment(
        "File Created By SMS Backup & Restore v10.21.004 on "
        + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )
    root.append(header)

    # Generate messages
    for i in range(num_messages):
        # Select contact based on their message probability
        contact = random.choices(
            contacts, weights=[c["message_prob"] for c in contacts], k=1
        )[0]

        # Generate message timestamp
        msg_date = start_date + (end_date - start_date) * random.random()

        # Create message
        sms = ET.SubElement(root, "sms")
        sms.set("protocol", "0")
        sms.set("address", contact["phone"])
        sms.set("date", str(int(msg_date.timestamp() * 1000)))
        sms.set(
            "type", "1" if random.random() < 0.5 else "2"
        )  # 1=received, 2=sent
        sms.set("subject", "null")
        sms.set("body", generate_message())
        sms.set("toa", "null")
        sms.set("sc_toa", "null")
        sms.set("service_center", "null")
        sms.set("read", "1")
        sms.set("status", "-1")
        sms.set("locked", "0")
        sms.set("date_sent", str(int(msg_date.timestamp() * 1000)))
        sms.set("sub_id", "-1")
        sms.set("readable_date", msg_date.strftime("%b %d, %Y %I:%M:%S %p"))
        sms.set("contact_name", contact["name"])

    # Pretty print XML
    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

    # Save to file
    with open("sample_backup.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    return contacts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate sample SMS backup data"
    )
    parser.add_argument(
        "--messages",
        type=int,
        default=1000,
        help="Number of messages to generate",
    )
    parser.add_argument(
        "--contacts",
        type=int,
        default=10,
        help="Number of contacts to generate",
    )

    args = parser.parse_args()

    contacts = create_sample_backup(args.messages, args.contacts)
    print(
        f"Generated {args.messages} messages across {args.contacts} contacts:"
    )
    for contact in contacts:
        print(f"- {contact['name']} ({contact['phone']})")
