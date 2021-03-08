# Необходимо написать Django приложение для работы с бинарным файлом, содержащем пары ключ/значение в определенном формате.

# Формат файла:
# key_size1|value_size1|key1|value1 ... key_sizeN|value_sizeN|keyN|valueN, где key_size и value_size 4 байтные беззнаковые числа, а key и value строки в кодировке unicode

# Для работы с файлом предоставить REST API, прдпочтительный формат тела запросов и ответов json. 
# Требуемый функционал:
# - добавлять, удалять пары ключ/значение
# - изменять значение по ключу
# - выводить список всех ключей
# - осуществлять поиск подстроки во всех значениях

# * добавить разграничение доступа к файлу - одна группа пользователей может делать только запросы для чтения,
# другая имеет полный доступ, неавторизованные - не имеют доступа
def add(key, value):
    with open('file.txt', 'ab') as f:
        f.write(len(key).to_bytes(4, 'big') + len(value).to_bytes(4, 'big') + key.encode('utf-8') + value.encode('utf-8'))

def exist(key):
    with open('file.txt', 'rb') as f:
        x = f.read()
        i = 0
        while i < len(x):
            key_len = int.from_bytes(x[i:i+4], 'big')
            value_len = int.from_bytes(x[i+4:i+8], 'big')
            key_value = x[i+8:i+8+key_len].decode('utf-8')
            if key_value == key:
                return True
            i += 8 + key_len + value_len
        return False

def get(key):
    with open('file.txt', 'rb') as f:
        x = f.read()
        i = 0
        while i < len(x):
            key_len = int.from_bytes(x[i:i+4], 'big')
            value_len = int.from_bytes(x[i+4:i+8], 'big')
            key_value = x[i+8:i+8+key_len].decode('utf-8')
            if key_value == key:
                value = x[i+8+key_len:i+8+key_len+value_len].decode('utf-8')
                return value
            i += 8 + key_len + value_len
        raise Exception("no such key")

def delete(key):
    x = None
    with open('file.txt', 'rb') as f:
        x = f.read()
    with open('file.txt', 'wb') as f:
        i = 0
        while i < len(x):
            # print(i)
            key_len = int.from_bytes(x[i:i+4], 'big')
            value_len = int.from_bytes(x[i+4:i+8], 'big')
            key_value = x[i+8:i+8+key_len].decode('utf-8')
            if key_value == key:
                f.write(x[:i] + x[i+8+key_len+value_len:])
                return x[i+8+key_len:i+8+key_len+value_len].decode('utf-8')
            i += 8 + key_len + value_len
        f.write(x)
        raise Exception("no such key")

def update(key, new_value):
    x = None
    with open('file.txt', 'rb') as f:
        x = f.read()
    with open('file.txt', 'wb') as f:
        i = 0
        while i < len(x):
            key_len = int.from_bytes(x[i:i+4], 'big')
            value_len = int.from_bytes(x[i+4:i+8], 'big')
            key_value = x[i+8:i+8+key_len].decode('utf-8')
            if key_value == key:
                encoded_pair = x[i:i+4] + len(new_value).to_bytes(4, 'big') + x[i+8:i+8+key_len] + new_value.encode('utf-8')
                f.write(x[:i] + encoded_pair + x[i+8+key_len+value_len:])
                return x[i + 8 + key_len:i + 8 + key_len + value_len].decode('utf-8')
            i += 8 + key_len + value_len
        f.write(x)
        raise Exception("no such value")

def list_all_keys():
    out = []
    with open('file.txt', 'rb') as f:
        x = f.read()
        i = 0
        while i < len(x):
            key_len = int.from_bytes(x[i:i+4], 'big')
            value_len = int.from_bytes(x[i+4:i+8], 'big')
            key_value = x[i+8:i+8+key_len].decode('utf-8')
            out.append(key_value)
            i += 8 + key_len + value_len
    return out

def find_substr(substr):
    out = []
    keys = list_all_keys()
    for key in keys:
        if substr in get(key):
            out.append(key)
    return out

def get_dict():
    out = {}
    keys = list_all_keys()
    for key in keys:
        out[key] = get(key)
    return out



if __name__ == "__main__":
    add("key5", "val")
    add("key6", "v")
    add("key7", "xxx")
    print(get_dict())
    print(find_substr("v"))
    delete("key5")
    delete("key6")
    delete("key7")
    print(list_all_keys())