from __future__ import annotations

import logging
from pathlib import Path
import json

from models.schemas import KnowledgeDocument
from services.config import BASE_DIR
from services.product_store import product_store
from services.product_knowledge_service import product_knowledge_service

logger = logging.getLogger(__name__)

# Product-specific guides and sections for the 5 default products
SEEDED_GUIDES = {
    "moss-router-x1": {
        "Mesh Pairing Guide": [
            ("Section 2.2: Wireless Node Pairing", 8, 
             "To pair a secondary node wirelessly, place it in the same room as the primary Moss Router X1, within 5-10 feet during setup. "
             "Power the node on and wait for the LED to pulse amber. Press the sync button on the back of the main router for 3 seconds "
             "until its LED flashes blue, then press sync on the secondary node. If pairing is successful, the secondary node LED will flash green."),
            ("Section 2.5: Troubleshooting Mesh Sync Failures", 12, 
             "If the secondary node fails to connect to the main router, the status light will pulse amber rapidly. "
             "This indicates a hardware synchronization failure. To resolve this, bring the node back to the same room as the main router. "
             "Perform a factory reset on the node by holding the reset button for 10 seconds. "
             "Attempt the pairing process again. Ensure that both units are running the same firmware version, as mismatching versions can cause sync failures.")
        ],
        "Troubleshooting Guide": [
            ("Section 3.1: Diagnosing Frequent Wireless Disconnections", 15, 
             "If your devices disconnect frequently from the Wi-Fi network, the issue is often Wi-Fi channel interference. "
             "To resolve this, log in to the router admin portal (http://192.168.1.1) and navigate to Wireless Settings. "
             "Change the 2.4GHz channel from 'Auto' to channel 1, 6, or 11. For the 5GHz band, select channel 36, 44, or 149. "
             "Additionally, reduce the channel width from 80MHz to 40MHz or 20MHz to significantly reduce channel congestion and increase stability.")
        ],
        "LED Status Reference": [
            ("Section 4.3: Solid Amber and Pulsing Amber Indicators", 22, 
             "A solid amber LED indicator means the router is booting up or initializing its operating system. "
             "Do not unplug the power adapter while the light is solid amber. "
             "A slowly pulsing amber LED indicator means the node is ready for pairing. "
             "A rapidly pulsing or blinking amber LED indicates a synchronization failure or a critical firmware warning. "
             "If it blinks amber, the node has lost connection to the main unit; move it closer to resolve.")
        ]
    },
    "hp-laserjet-pro-m404n": {
        "User Guide": [
            ("Section 1.5: Print Quality Issues", 12, 
             "If the print output appears faded, uneven, or has white vertical streaks, the toner cartridge may be running low. "
             "Remove the toner cartridge from the front door assembly, hold it by the ends, and gently shake it from side to side 5-6 times "
             "to redistribute the remaining toner. Reinsert the cartridge and perform a test print. If fading persists, replace the cartridge with HP 58A or 58X."),
            ("Section 3.2: Reordering Supplies", 35, 
             "If the printer's LCD panel displays a 'Toner Low' warning or the orange status light flashes, it is time to order a replacement. "
             "The HP LaserJet Pro M404n uses HP 58A (standard yield, ~3,000 pages) or HP 58X (high yield, ~10,000 pages) black toner cartridges. "
             "Always use original HP toner to prevent print defects and drum damage.")
        ],
        "Troubleshooting Manual": [
            ("Section 2.3: Clearing Paper Jams", 27, 
             "When a paper jam occurs, the printer halts printing and displays an error code. "
             "Open the rear access door and check for jammed sheets in the fuser area. "
             "Gently pull any jammed paper straight out of Tray 2 or the rear area. "
             "Do not pull paper from the output bin if possible, as this can damage the internal rollers. Reset Tray 2 to resume."),
            ("Section 4.1: Network Setup Troubleshooting", 40, 
             "If the printer shows a connection timeout or offline status on your PC, inspect the Ethernet cable connection. "
             "Verify the cable is plugged into both the printer LAN port and the network router. "
             "Confirm the green link light on the printer's RJ45 port is solid or blinking. "
             "Print a configuration report via the printer control panel to confirm the assigned IP address.")
        ]
    },
    "smart-air-conditioner": {
        "Owner Operation Manual": [
            ("Section 2.1: Cold Air Issues", 14, 
             "If the smart AC is not cooling the room despite running, the air filters may be clogged. "
             "Clogged filters restrict airflow and reduce cooling efficiency. "
             "Open the front cover, slide out the plastic filters, wash them with mild soap and warm water, and dry completely before reinserting. "
             "Clean the filters every 2 weeks for optimal climate control performance."),
            ("Section 1.3: Remote Control Pairing", 5, 
             "If the remote control is unresponsive, confirm the battery orientation and verify the screen displays the active temperature. "
             "Point the remote directly at the receiver window on the AC indoor unit. "
             "The maximum range is 20 feet. If the receiver beep does not sound, replace the AAA batteries and check if the timer indicator light on the AC is blinking.")
        ],
        "Service & Installation Guide": [
            ("Section 3.4: Drain Hose Maintenance", 25, 
             "Water leakage from the base of the indoor AC unit is caused by blockages in the condensate drain pipe. "
             "Over time, dust and algae build up in the drain hose, preventing water flow. "
             "Ensure the drain hose slopes downwards continuously with no bends. "
             "Flush the drain hose with warm water or clear obstructions using a soft wire to resolve indoor condensation drips."),
            ("Section 4.2: Fan and Blower Diagnostics", 31, 
             "Strange clicking or rattling noises from the AC indoor unit usually indicate loose fan motor mountings or a dirty blower wheel. "
             "Ensure the unit is shut off, open the intake grill, and visually inspect for debris inside the drum. "
             "If the fan blades are clean and mounting screws are tight, the fan bearing may need replacement.")
        ]
    },
    "smart-washing-machine": {
        "User Manual": [
            ("Section 3.1: Drum Spin Issues", 18, 
             "If the washing machine stops and refuses to spin, the load may be unbalanced. "
             "A single heavy item, like a towel or rug, can offset the balance of the drum. "
             "Pause the cycle, open the door, redistribute the clothes evenly inside the drum, and press Start. "
             "An unbalanced load will trigger a 'UE' or 'Ub' error code on the control display panel."),
            ("Section 1.4: Leveling Feet Calibration", 8, 
             "Excessive shaking, banging, and vibration during the spin cycle is caused by unlevel placement. "
             "Place a bubble level on top of the washing machine. "
             "Loosen the lock nuts on the leveling feet at the bottom corners, adjust the height until the cabinet is perfectly level, "
             "and retighten the lock nuts securely to prevent the washer from moving during high-speed spins.")
        ],
        "Component Diagnostic Manual": [
            ("Section 4.2: Pump Filter Maintenance", 22, 
             "If the washer is not draining water, the drain pump filter is likely clogged with lint, coins, or small items. "
             "Locate the service filter door at the bottom right corner of the front panel. "
             "Place a shallow pan on the floor, release the black emergency drain tube to empty water, "
             "then twist the pump filter counter-clockwise and pull it out. Clear any trapped debris and screw it back on tight."),
            ("Section 2.5: Door Lock Emergency Release", 11, 
             "If the washer door remains locked after the cycle completes and water has drained, the safety solenoid is stuck. "
             "Unplug the washing machine from the wall outlet and wait 5 minutes. "
             "If the door is still locked, open the drain filter door, locate the plastic pull tab, "
             "and pull it downwards gently to manually bypass the door lock mechanism.")
        ]
    },
    "water-purifier": {
        "Instruction Manual": [
            ("Section 2.2: Flow Rate Troubles", 10, 
             "A low water flow rate from the purifier faucet is caused by low water feed pressure or clogged pre-filters. "
             "Ensure the feed valve is fully open and the incoming pressure is at least 30 psi. "
             "If input pressure is sufficient, replace the sediment and carbon block filters. "
             "Accumulated silt and chlorine by-products reduce water delivery speed over time."),
            ("Section 3.1: Filter Replacement Schedule", 15, 
             "To maintain water purity, replace the pre-filter, sediment filter, and activated carbon block filter every 6 months. "
             "The main Reverse Osmosis (RO) membrane should be replaced every 12 to 24 months depending on input TDS levels. "
             "Always flush new filters for 10 minutes before directing output water to the holding tank.")
        ],
        "RO Membrane Calibration Guide": [
            ("Section 5.3: TDS Sensor Probe and RO Membrane Quality", 32, 
             "A blinking TDS (Total Dissolved Solids) alarm indicates that the purification rate has dropped. "
             "If the purified water TDS exceeds 10% of raw input water TDS, the RO membrane reject rate is below 90%. "
             "Inspect the RO membrane for tears, flush the membrane chamber, and check if the TDS sensor probe is clean. "
             "If the membrane is older than 18 months, replace it and reset the filter indicator button.")
        ]
    }
}

async def seed_all_documents() -> None:
    local_path = Path(BASE_DIR) / "storage" / "local_indexed_documents.json"
    
    # Check if we already seeded our default products
    has_seeds = False
    if local_path.exists() and local_path.stat().st_size > 0:
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Check if we have documents for hp-laserjet-pro-m404n or other default products
            has_seeds = any("hp-laserjet-pro-m404n" in key for key in data.keys())
        except Exception:
            has_seeds = False
            
    if has_seeds:
        logger.info("Local fallback store is already seeded. Skipping document seeding.")
        return
        
    logger.info("=== SEEDING DETAILED PRODUCT MANUALS ===")
    
    seeded_docs = []
    
    for product_id, guides in SEEDED_GUIDES.items():
        try:
            product = product_store.get_product(product_id)
        except Exception:
            logger.warning("Product not found during seeding: %s", product_id)
            continue
            
        for guide_title, sections in guides.items():
            for sec_title, page_num, text_content in sections:
                # Store guide/section/page meta
                doc_title = f"{guide_title} | {sec_title} | Page {page_num}"
                
                # Build KnowledgeDocument chunks
                chunks = product_knowledge_service.build_documents(
                    product=product,
                    text=text_content,
                    source_type="text",
                    title=doc_title,
                    filename=f"{guide_title.lower().replace(' ', '_')}.txt"
                )
                
                # Add page and section to metadata of each chunk
                for chunk in chunks:
                    chunk.metadata["section"] = sec_title
                    chunk.metadata["page"] = str(page_num)
                    chunk.metadata["title"] = guide_title
                    seeded_docs.append(chunk)
                    
    # Write to local file
    if seeded_docs:
        try:
            data = {}
            if local_path.exists() and local_path.stat().st_size > 0:
                with open(local_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            for doc in seeded_docs:
                data[doc.id] = {
                    "id": doc.id,
                    "text": doc.text,
                    "metadata": doc.metadata
                }
                
            tmp_path = local_path.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            tmp_path.replace(local_path)
            logger.info("Successfully seeded %d detailed manual chunks locally.", len(seeded_docs))
        except Exception as exc:
            logger.error("Failed to write seed documents: %s", exc)
