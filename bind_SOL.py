import random

import requests
from eth_account.messages import encode_defunct
from web3 import Web3

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def write_line(line):
    with open('fail.txt', 'a') as file:
        file.write(line+'\n')
def bind_sol(evm_address,evm_key,sol,proxy):
    http_provider = 'https://unichain-rpc.publicnode.com'
    web3 = Web3(Web3.HTTPProvider(http_provider))

    message = f'PumpDAO: {sol}'
    account = web3.eth.account.from_key(evm_key)
    signature = account.sign_message(encode_defunct(text=message)).signature.hex()
    url = 'https://api.pumpdao.dev/api/v1/bind'

    data = {
        'evm_address': evm_address,
        'evm_sign': signature,
        'sol_address':sol
    }

    proxy = {
        'https': proxy,
        'http': proxy
    }
    try:
        res = requests.post(url, json=data,proxies=proxy)
        print(res.text)
        if res.json()['code'] == 0 or res.json()['code']== 10010 :
            logging.info(f'绑定成功')
        else:
            logging.info(f'绑定失败,失败EVM地址为:{evm_address},sol地址为:{sol}')
            content = f'{evm_address},{evm_key},{sol}'
            write_line(content)
            # write_line('fail.txt',f'{evm_address},{sol}')

    except Exception as e:
        logging.info(f'出现异常绑定失败，EVM地址为：{evm_address},sol地址为:{sol}')
        content = f'{evm_address},{evm_key},{sol}'
        write_line(content)
        logging.info(e)

def handle():
    evm_lines = open('evm_wallets.txt','r',encoding='utf-8').readlines()
    sol = open('sol_address.txt','r',encoding='utf-8').readlines()
    nums = len(evm_lines)
    evm_address_list = []
    evm_key_list = []
    sol_address_list = []
    proxy_list = []
    for line in evm_lines:
        address,key = line.strip().split(',')
        evm_address_list.append(address)
        evm_key_list.append(key)

    for line in sol:
        sol = line.strip()
        sol_address_list.append(sol)

    proxies_lines = open('proxy.txt', 'r', encoding='utf-8').readlines()
    for line in proxies_lines:
        proxy = line.strip()
        proxy_list.append(proxy)

    #
    for i in range(nums):
        print(f'正在运行第{i+1}/{nums}个')
        if proxy_list is not None:
            proxy = random.choice(proxy_list)
        else:
            proxy = None
        bind_sol(evm_address_list[i],evm_key_list[i],sol_address_list[i],proxy)

    while True:
        evm_address_list = []
        evm_key_list = []
        sol_address_list = []
        lines = open('fail.txt', 'r', encoding='utf-8').readlines()
        nums = len(lines)
        logging.info(f'失败绑定地址数为:{nums},正在尝试再次绑定')
        if nums == 0:
            return
        for line in lines:

            address = line.strip().split(',')[0]
            key = line.strip().split(',')[1]
            sol = line.strip().split(',')[2]
            evm_address_list.append(address)
            evm_key_list.append(key)
            sol_address_list.append(sol)

        #fail.txt数据清零
        open('fail.txt','w',encoding='utf-8').write('')

        for i in range(nums):
            print(f'正在运行第{i + 1}/{nums}个')
            if proxy_list is not None:
                proxy = random.choice(proxy_list)
            else:
                proxy = None
            bind_sol(evm_address_list[i], evm_key_list[i], sol_address_list[i], proxy)

if __name__ == '__main__':
    handle()