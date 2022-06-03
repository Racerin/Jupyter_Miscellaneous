import albionTest as AT
import logging

logging.basicConfig(level=logging.DEBUG,
#filename= 'output.txt',
format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Start of albionBot.py")

if __name__ == "__main__":
    AT.mane()