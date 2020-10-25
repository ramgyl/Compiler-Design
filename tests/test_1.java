import java.io.*;
public class Complex extends Object {

private double u;
private double v;
/*
*
*/
Complex (double x, double y) {

u=x;
v=y;

}

public double Real () {

return u;

}

public double Imaginary () {

return v;

}
public double Magnitude () {

return Math.sqrt(u*u + v*v);

}

public double Arg () {

return Math.atan2(v, u);

}

// Add z to w; i.e. w += z
public Complex Plus (Complex z) {
return new Complex(u+z.u,v+z.v);

}

// Subtract z from w
public Complex Minus (Complex z) {

return new Complex(u-z.u,v-z.v);

}

public Complex Times (Complex z) {

return new Complex(u*z.u-v*z.v,u*z.v+v*z.u);

}

// divide w by z
public Complex DivideBy (Complex z) {

double rz = z.Magnitude();

return new Complex((u*z.u+v*z.v)/(rz*rz),(v*z.u-u*z.v)/(rz*rz));

}

}

/*Notice especially that u and v are now private. They cannot be accessed by external code even if we want them to be.

*The use of one of these methods will look like the following. Add the following ComplexExamples class to the Complex.java file and compile. Then run ComplexExamples in the usual way by typing java ComplexExamples.
*/
//Complex Arithmetic Examples
class ComplexExamples {

public static void main (String args[]) {

System.out.println(_234);
Complex u, v, w, z;

u = new Complex(1,2);
System.out.println("u: "+u.Real()+" + "+u.Imaginary()+"i");
v = new Complex(3,-4.5);
System.out.println("v: " + v.Real() + " + " + v.Imaginary() + "i");

// Add u + v;
z=u.Plus(v);
System.out.println("u + v: "+ z.Real() + " + " + z.Imaginary() + "i");
// Add v + u;
z=v.Plus(u);
System.out.println("v + u: "+ z.Real() + " + " + z.Imaginary() + "i");

z=u.Minus(v);
System.out.println("u - v: "+ z.Real() + " + " + z.Imaginary() + "i");
z=v.Minus(u);
System.out.println("v - u: "+ z.Real() + " + " + z.Imaginary() + "i");

z=u.Times(v);
System.out.println("u * v: "+ z.Real() + " + " + z.Imaginary() + "i");
z=v.Times(u);
System.out.println("v * u: "+ z.Real() + " + " + z.Imaginary() + "i");

z=u.DivideBy(v);
System.out.println("u / v: "+ z.Real() + " + " + z.Imaginary() + "i");
z=v.DivideBy(u);
System.out.println("v / u: "+ z.Real() + " + " + z.Imaginary() + "i");

}

}