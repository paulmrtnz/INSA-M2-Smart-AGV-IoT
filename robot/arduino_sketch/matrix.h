
extern unsigned char smile[16];

#define SCL_Pin A5  //set a pin of clock to A5
#define SDA_Pin A4  //set a data pin to A4

// Initialisation de la matrice LED
void setup_led_matrix(void);

// Afficher une trame de 16 octets sur la matrice LED
void matrix_display(unsigned char []);

//the condition that data starts transmitting
void IIC_start(void);
//the sign that transmission of data ends
void IIC_end(void);
//transmit data
void IIC_send(unsigned char);