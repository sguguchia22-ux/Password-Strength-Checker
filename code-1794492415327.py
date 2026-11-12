import math
import string
import time
import itertools
import re

# პოპულარული/გაჟონილი პაროლების მცირე სატესტო ბაზა (Dictionary Attack-ის სიმულაციისთვის)
COMMON_PASSWORDS = {
    "123456", "password", "12345678", "qwerty", "12345", "123456789",
    "admin", "admin123", "admin@123", "password123", "111111", "iloveyou",
    "welcome", "monkey", "dragon", "letmein", "football", "2025", "2026"
}

def calculate_charset_size(password: str) -> tuple[int, str]:
    """საზღვრავს პაროლში გამოყენებული სიმბოლოთა სიმრავლის ზომას (R) და ტიპებს."""
    charset_size = 0
    used_types = []

    if any(c in string.ascii_lowercase for c in password):
        charset_size += 26
        used_types.append("პატარა ასოები (a-z)")
    if any(c in string.ascii_uppercase for c in password):
        charset_size += 26
        used_types.append("დიდი ასოები (A-Z)")
    if any(c in string.digits for c in password):
        charset_size += 10
        used_types.append("ციფრები (0-9)")
    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)  # 32 სპეციალური სიმბოლო
        used_types.append("სპეციალური სიმბოლოები (!@#$)")

    return charset_size, ", ".join(used_types) if used_types else "უცნობი სიმბოლოები"

def format_time(seconds: float) -> str:
    """გარდაქმნის წამებს ადამიანისთვის ადვილად აღსაქმელ დროის ერთეულებში."""
    if seconds < 0.001:
        return "მყისიერად (< 1 მილიწამი)"
    elif seconds < 60:
        return f"{seconds:.2f} წამი"
    elif seconds < 3600:
        return f"{seconds / 60:.2f} წუთი"
    elif seconds < 86400:
        return f"{seconds / 3600:.2f} საათი"
    elif seconds < 31536000:
        return f"{seconds / 86400:.2f} დღე"
    else:
        years = seconds / 31536000
        if years > 1_000_000_000:
            return f"{years:.2e} წელი (პრაქტიკულად გაუტეხავი)"
        return f"{years:,.0f} წელი"

def analyze_password(password: str):
    """მოდული 1: პაროლის სიმძლავრის, ენტროპიისა და სუსტი პატერნების ანალიზი."""
    print("\n" + "=" * 65)
    print("🛡️  მოდული 1: პაროლის სიმძლავრისა და ენტროპიის ანალიზი")
    print("=" * 65)

    length = len(password)
    charset_size, types_str = calculate_charset_size(password)

    # ენტროპიის გამოთვლა ფორმულით: E = L * log2(R)
    entropy = length * math.log2(charset_size) if charset_size > 0 else 0

    # სუსტი პატერნების (ევრისტიკული) შემოწმება
    warnings = []
    if password.lower() in COMMON_PASSWORDS:
        warnings.append("პაროლი მოიძებნა გაჟონილი პაროლების ლექსიკონში (Dictionary Attack რისკი)!")
    if length < 8:
        warnings.append("პაროლი ძალიან მოკლეა (რეკომენდებულია მინიმუმ 12-14 სიმბოლო).")
    if re.search(r"(.)\1\1", password):
        warnings.append("შეიცავს ერთი და იმავე სიმბოლოს განმეორებას (მაგ., 'aaa' ან '111').")
    if re.search(r"(1234|2345|3456|4567|5678|6789|abcd|qwerty)", password.lower()):
        warnings.append("შეიცავს კლავიატურის ან ციფრების სტანდარტულ თანმიმდევრობას.")

    # სიძლიერის კატეგორიის განსაზღვრა
    if password.lower() in COMMON_PASSWORDS or entropy < 28:
        strength = "🔴 ძალიან სუსტი (Very Weak)"
    elif entropy < 50:
        strength = "🟠 სუსტი (Weak)"
    elif entropy < 75:
        strength = "🟡 საშუალო (Moderate)"
    elif entropy < 100:
        strength = "🟢 ძლიერი (Strong)"
    else:
        strength = "💎 კრიპტოგრაფიულად მდგრადი (Very Strong)"

    # სავარაუდო გატეხვის დრო თანამედროვე GPU-ზე (დაშვება: 10 მილიარდი ჰეში წამში)
    total_combinations = charset_size ** length if charset_size > 0 else 0
    gpu_speed = 10_000_000_000  # 10^10 კომბინაცია წამში
    estimated_seconds = (total_combinations / 2) / gpu_speed

    print(f"🔹 პაროლის სიგრძე (L):        {length} სიმბოლო")
    print(f"🔹 სიმბოლოთა სიმრავლე (R):    {charset_size} ({types_str})")
    print(f"🔹 ინფორმაციული ენტროპია:     {entropy:.2f} ბიტი")
    print(f"🔹 შეფასების სტატუსი:         {strength}")
    print(f"🔹 სავარაუდო კომბინაციები:    {total_combinations:,}")
    print(f"⏱️  გატეხვის დრო (GPU 10B/წმ): {format_time(estimated_seconds)}")

    if warnings:
        print("\n⚠️  აღმოჩენილი სისუსტეები და რეკომენდაციები:")
        for w in warnings:
            print(f"   • {w}")
    else:
        print("\n✅ შესანიშნავია! სტრუქტურული სისუსტეები არ აღმოჩნდა.")

def simulate_brute_force(target_password: str):
    """მოდული 2: რეალური Brute-Force შეტევის სიმულაცია."""
    print("\n" + "=" * 65)
    print("⚙️  მოდული 2: Brute-Force შეტევის რეალური სიმულაცია")
    print("=" * 65)

    # პირველ რიგში ვამოწმებთ ლექსიკონით შეტევას (Dictionary Attack)
    print("🔍 ეტაპი 1: ლექსიკონით შეტევის (Dictionary Attack) შემოწმება...")
    time.sleep(0.6)
    if target_password.lower() in COMMON_PASSWORDS:
        print(f"💥 პაროლი '{target_password}' მყისიერად გატყდა ლექსიკონის ბაზით (0.0001 წამში)!")
        return

    print("   ➜ ლექსიკონში ვერ მოიძებნა. გადავდივართ სრულ გადარჩევაზე (Exhaustive Search)...")

    # უსაფრთხოების ზღვარი: დემონსტრაციისას რეალურ გადარჩევას ვაკეთებთ მაქსიმუმ 4 სიმბოლოზე,
    # რათა პროგრამა საათობით არ გაიჭედოს წარდგენის დროს.
    if len(target_password) > 4:
        print(f"\nℹ️  პაროლის სიგრძეა {len(target_password)} სიმბოლო.")
        print("   დემონსტრაციის რეჟიმში რეალურ დროში გადარჩევა შეზღუდულია 4 სიმბოლომდე,")
        print("   რადგან უფრო გრძელი პაროლის სრულ გადარჩევას თქვენი პროცესორი (CPU) დიდ დროს მოანდომებს.")
        print("   (რეალური დროის გათვლა იხილეთ ზემოთ, მოდულ 1-ში).")
        return

    # სიმბოლოთა ბაზის შერჩევა სიმულაციისთვის
    charset = ""
    if any(c in string.digits for c in target_password):
        charset += string.digits
    if any(c in string.ascii_lowercase for c in target_password):
        charset += string.ascii_lowercase
    if any(c in string.ascii_uppercase for c in target_password):
        charset += string.ascii_uppercase
    if any(c in string.punctuation for c in target_password):
        charset += string.punctuation

    print(f"🚀 ეტაპი 2: მიმდინარეობს კომბინაციების გენერირება ({len(charset)} სიმბოლოიანი ბაზიდან)...")
    start_time = time.time()
    attempts = 0

    for length in range(1, len(target_password) + 1):
        for guess_tuple in itertools.product(charset, repeat=length):
            attempts += 1
            guess = "".join(guess_tuple)
            if guess == target_password:
                elapsed_time = time.time() - start_time
                speed = attempts / elapsed_time if elapsed_time > 0 else attempts
                print(f"\n💥 წარმატება! პაროლი ნაპოვნია: '{guess}'")
                print(f"🔢 სულ განხორციელდა მცდელობა: {attempts:,}")
                print(f"⏱️  დახარჯული რეალური დრო:     {elapsed_time:.4f} წამი")
                print(f"⚡ CPU-ს სიჩქარე სიმულაციაში: {speed:,.0f} კომბინაცია/წამში")
                return

def main():
    print("\n🔐 PASSWORD STRENGTH CHECKER & BRUTE-FORCE SIMULATOR")
    print("ავტორი: სალომე გუგუჩია | საგანმანათლებლო პროექტი კიბერუსაფრთხოებაში")
    print("შენიშვნა: პროგრამა მუშაობს ლოკალურად, შეყვანილი მონაცემები არსად ინახება.")

    while True:
        print("\n" + "-" * 65)
        print("აირჩიეთ რეჟიმი:")
        print("  [1] სწრაფი დემო (პრეზენტაციის 3 სატესტო სცენარის გაშვება)")
        print("  [2] საკუთარი პაროლის შემოწმება")
        print("  [0] გამოსვლა")
        choice = input("თქვენი არჩევანი (1/2/0): ").strip()

        if choice == "1":
            demo_passwords = ["2026", "Admin@123", "Kiber#Gori_2026!"]
            for idx, pwd in enumerate(demo_passwords, 1):
                print(f"\n\n>>> სატესტო სცენარი #{idx}: '{pwd}' <<<")
                analyze_password(pwd)
                simulate_brute_force(pwd)
                if idx < len(demo_passwords):
                    input("\n[დააჭირეთ Enter-ს შემდეგ სცენარზე გადასასვლელად...]")
        elif choice == "2":
            user_pwd = input("\nშეიყვანეთ შესამოწმებელი პაროლი: ")
            if not user_pwd:
                print("⚠️ პაროლი ცარიელია!")
                continue
            analyze_password(user_pwd)
            simulate_brute_force(user_pwd)
        elif choice == "0":
            print("\nპროგრამა დასრულდა. გმადლობთ!")
            break
        else:
            print("⚠️ არასწორი არჩევანი, სცადეთ თავიდან.")

if __name__ == "__main__":
    main()
