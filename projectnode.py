import raftos
import asyncio
import argparse
import aiomysql

PORTS = [8000, 8001, 8002]

parser = argparse.ArgumentParser()
parser.add_argument('--node')
args = parser.parse_args()

NODE_ID = int(args.node)

PORT = PORTS[NODE_ID-1]
NODE_LOGFILE = f'node{NODE_ID}_CUSTOMLOG.log'
# Since this is run for each 'node', we're telling this node
# what ports the other nodes are running on.
other_nodes_ports = [p for p in [8000, 8001, 8002] if p != PORT]

raftos.configure({
    'log_path': './',
    'serializer': raftos.serializers.JSONSerializer
})
loop = asyncio.get_event_loop()

# Each port is simulating a real life
# node/machine connected over a network.
this_node_address = f'127.0.0.1:{PORT}'

loop.create_task(
    raftos.register(
        this_node_address,

        # Telling raft which ones are 
        # part of this node's cluster
        cluster=[
            f'127.0.0.1:{other_nodes_ports[0]}',
            f'127.0.0.1:{other_nodes_ports[1]}'
        ]
    )
)

with open(NODE_LOGFILE, 'w') as log_file:
    pass

async def run(loop):
    VARIABLE = raftos.Replicated(name='VARIABLE')

    # Non leaders get stuck in this loop!
    old_leader = None
    while raftos.get_leader() != this_node_address:

        await asyncio.sleep(5)

        with open(NODE_LOGFILE, 'a') as log_file:
            current_leader = raftos.get_leader()
            if current_leader != old_leader:
                log_file.write(f'Leader is now: {current_leader}\n')
            old_leader = current_leader

    # A node that reaches here has to be the leader.
    await asyncio.sleep(5)

    with open(NODE_LOGFILE, 'a') as log_file:

        # Connecting to MySQL database
        async with aiomysql.create_pool(host='localhost', port=3306,
                                        user='root', password='Dbms1234$',
                                        db='raft_connection', loop=loop) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Example query: Selecting data from a table named 'your_table'
                    await cursor.execute("SELECT * FROM tasks")
                    result = await cursor.fetchall()
                    log_file.write("Data from MySQL table:\n")
                    for row in result:
                        log_file.write(f"{row}\n")

        # This block of code simulates a CLIENT telling v
        # this CLUSTER that it wants to set the value of 
        # the variable 'VARIABLE' to something specific

        # This specific code initially sets the value to
        # 'PES2UG20CS182' if it hasn't been set before,
        # and to the next value once the next leader enters
        # this block of code and realizes that the value
        # has already been set before
        try:
            old_value = await VARIABLE.get()
            if old_value is not None:
                await VARIABLE.set('HashCode')
            else:
                await VARIABLE.set('PES2UG21CS055') 
        except:
            await VARIABLE.set('PES2UG21CS055')

        # Client Command executed;    
        log_file.write('Done writing VARIABLE\n Check the .log and .state_machine files!')


loop.run_until_complete(run(loop))
loop.run_forever()
