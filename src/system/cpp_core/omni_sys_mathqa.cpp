extern "C" {
    struct Rational {
        int numerator;
        int denominator;
    };

    int gcd(int a, int b) {
        while (b != 0) {
            int temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    Rational omni_sys_mathqa_add_rational(Rational a, Rational b) {
        Rational res;
        res.numerator = a.numerator * b.denominator + b.numerator * a.denominator;
        res.denominator = a.denominator * b.denominator;
        
        int div = gcd(res.numerator, res.denominator);
        res.numerator /= div;
        res.denominator /= div;
        
        if (res.denominator < 0) {
            res.numerator = -res.numerator;
            res.denominator = -res.denominator;
        }
        return res;
    }
}
