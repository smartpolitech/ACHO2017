/** \mainpage RoboComp Interfaces: Persiana.ice
 *
* Interfaz para la comunicación con el componente
* persiana en el sistema ACHO.
* Sistemas Multimedia.Curso 2016/17
*                                                                   
* 
*                                                                                              
*    PORT  <br>   
*/
#ifndef PERSIANA_ICE
#define PERSIANA_ICE

/** \namespace Persiana
  *@brief Name space Generic
  */
module RoboCompPersiana
{
  /** \interface Generic
  *@brief interface Generic
  */ 	
  interface Persiana
  {
  	void subir();
  	void bajar();
  	void parar();
  };
};

#endif