from faker import Faker


if __name__ == '__main__':
    f = Faker(["ru_RU"])
    print(f.simple_profile())