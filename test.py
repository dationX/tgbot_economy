def calculate():
    print("Введите два числа и выберите операцию.")
    try:
        num1 = int(input("Введите первое число: "))
        num2 = int(input("Введите второе число: "))
    except ValueError:
        print("Введите корректные числа!")
        return
    
    operation = input("Выберите операцию (+, -, *, /): ")

    if operation == '+':
        print(f"Результат: {num1} + {num2} = {num1 + num2}")
    elif operation == '-':
        print(f"Результат: {num1} - {num2} = {num1 - num2}")
    elif operation == '*':
        print(f"Результат: {num1} * {num2} = {num1 * num2}")
    elif operation == '/':
        print(f"Результат: {num1} / {num2} = {num1 / num2}")

    else:
        print("Неизвестная операция.")

calculate()