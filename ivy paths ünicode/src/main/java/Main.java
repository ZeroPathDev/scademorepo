import org.apache.commons.collections.Bag;
import org.apache.commons.collections.bag.HashBag;

public class Main {
    public static void main(String[] args) {
        Bag counts = new HashBag();
        counts.add("policy");
        System.out.println(counts.getCount("policy"));
    }
}
