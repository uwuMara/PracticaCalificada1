import java.io.*;
import java.net.*;
import java.sql.*;

public class Servidor {

    static String host = System.getenv("DB_HOST");
    static String user = System.getenv("DB_USER");
    static String pass = System.getenv("DB_PASS");

    public static void main(String[] args) throws Exception {

        ServerSocket server = new ServerSocket(5005);
        System.out.println("Servidor corriendo en puerto 5005...");

        while (true) {
            Socket socket = server.accept();
            new Thread(() -> manejarCliente(socket)).start();
        }
    }

    public static void manejarCliente(Socket socket) {
        try {
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);

            String request = in.readLine();

            if (request.startsWith("PRODUCTO")) {
                crearProducto(request, out);
            } else if (request.startsWith("PEDIDO")) {
                registrarPedido(request, out);
            }

            socket.close();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // =========================
    // CREAR PRODUCTO
    // =========================
    public static void crearProducto(String request, PrintWriter out) {
        try {
            String[] p = request.split(",");
            String nombre = p[1];
            double precio = Double.parseDouble(p[2]);
            int stock = Integer.parseInt(p[3]);

            Connection conn = conectar();

            PreparedStatement ps = conn.prepareStatement(
                "INSERT INTO productos (NombreProducto, PrecioUnidad, UnidadesEnExistencia) VALUES (?, ?, ?)"
            );

            ps.setString(1, nombre);
            ps.setDouble(2, precio);
            ps.setInt(3, stock);

            ps.executeUpdate();

            out.println("Producto creado");
            conn.close();

        } catch (Exception e) {
            out.println("Error al crear producto");
            e.printStackTrace();
        }
    }

    // =========================
    // REGISTRAR PEDIDO (TRANSACCIÓN)
    // =========================
    public static void registrarPedido(String request, PrintWriter out) {
        Connection conn = null;

        try {
            String[] p = request.split(",");
            String cliente = p[1];
            int productId = Integer.parseInt(p[2]);
            int cantidad = Integer.parseInt(p[3]);

            conn = conectar();
            conn.setAutoCommit(false);

            // 1. Crear pedido
            PreparedStatement ps1 = conn.prepareStatement(
                "INSERT INTO pedidos (IdCliente, FechaPedido) VALUES (?, NOW())",
                Statement.RETURN_GENERATED_KEYS
            );

            ps1.setString(1, cliente);
            ps1.executeUpdate();

            ResultSet rs = ps1.getGeneratedKeys();
            rs.next();
            int orderId = rs.getInt(1);

            // 2. Verificar stock
            PreparedStatement ps2 = conn.prepareStatement(
                "SELECT UnidadesEnExistencia FROM productos WHERE IdProducto=? FOR UPDATE"
            );

            ps2.setInt(1, productId);
            ResultSet rs2 = ps2.executeQuery();

            if (rs2.next()) {
                int stock = rs2.getInt(1);

                if (stock >= cantidad) {

                    // 3. Insertar detalle
                    PreparedStatement ps3 = conn.prepareStatement(
                        "INSERT INTO detalle (IdPedido, IdProducto, Cantidad, PrecioUnidad) VALUES (?, ?, ?, ?)"
                    );

                    ps3.setInt(1, orderId);
                    ps3.setInt(2, productId);
                    ps3.setInt(3, cantidad);
                    ps3.setDouble(4, 0);

                    ps3.executeUpdate();

                    // 4. Actualizar stock
                    PreparedStatement ps4 = conn.prepareStatement(
                        "UPDATE productos SET UnidadesEnExistencia = UnidadesEnExistencia - ? WHERE IdProducto=?"
                    );

                    ps4.setInt(1, cantidad);
                    ps4.setInt(2, productId);
                    ps4.executeUpdate();

                    conn.commit();
                    out.println("Pedido registrado");

                } else {
                    conn.rollback();
                    out.println("Stock insuficiente");
                }
            } else {
                conn.rollback();
                out.println("Producto no existe");
            }

        } catch (Exception e) {
            try {
                if (conn != null) conn.rollback();
            } catch (Exception ex) {}

            out.println("Error en pedido");
            e.printStackTrace();
        } finally {
            try {
                if (conn != null) conn.close();
            } catch (Exception ex) {}
        }
    }

    // =========================
    // CONEXIÓN BD
    // =========================
    public static Connection conectar() throws Exception {
        String url = "jdbc:mysql://" + host + ":3306/neptuno";
        return DriverManager.getConnection(url, user, pass);
    }
}

