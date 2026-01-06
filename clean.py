"""
dARK 2.0 - Clean Script
Removes deployed contracts configuration
"""
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DEPLOYED_CONFIG = os.path.join(PROJECT_ROOT, 'deployed_contracts.ini')


def main():
    logging.info("dARK 2.0 - Clean")
    
    try:
        os.remove(DEPLOYED_CONFIG)
        logging.info(f"Removed: {DEPLOYED_CONFIG}")
        logging.info("System is clean!")
    except FileNotFoundError:
        logging.info("System is already clean!")


if __name__ == "__main__":
    main()