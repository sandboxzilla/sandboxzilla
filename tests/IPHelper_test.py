from sandboxzilla import IPHelper

if __name__ == '__main__':
    _comm_obj = IPHelper(file_name='ip', date_filename=False)

    def on_in(pkt):
        data = pkt['payload']
        if data is not None and len(data) > 0:
            _comm_obj.debug_write(topic='Received',
                                 data=data.replace('\n', '').replace('\r', ''))

    _comm_obj.open(address='127.0.0.1:2000').start(name='ipHelper_utest', call_back=on_in)
    try:
        _comm_obj.beacon(frequency=0.3)
    except KeyboardInterrupt:
        print('\nRemember me fondly!')
    finally:
        _comm_obj.close()
