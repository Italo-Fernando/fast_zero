from asyncio import gather, run, sleep


async def corrotina(n):
    print(f'Iniciando corrotina {n}')
    await sleep(1)
    print(f'Retomando corrotina {n}')
    await sleep(1)
    print(f'Retomando corrotina {n}')
    await sleep(1)
    print(f'Corrotina {n} finalizada')


async def main():
    await gather(corrotina(1), corrotina(2))


run(main())
