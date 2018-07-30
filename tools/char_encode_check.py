_enc_list = ["utf-8", "cp1252", "cp437"]

def check(data):
    if 'encoding' in data:
        enc = data['encoding']
        if enc in _enc_list:
            return enc
        else:
            print("[E]", enc, "is not a valid encoding.")
    else:
        print("[ ] No 'encoding' key found, guessing character encoding.")
        for e in _enc_list:
            try:
                f = open('./raw/' + data['file'], encoding=e)
                for line in f:
                    pass
                print("[ ] No decoding error with ", e, ".", sep='')
                f.close()
                return e
            except UnicodeDecodeError:
                f.close()
        print("[E] Could not guess original character encoding.")
        exit(1)
