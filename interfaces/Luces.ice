/** \mainpage RoboComp Interfaces: Luces.ice
 *
 * \section intro_sec Introduction
* Interface for Luces component. 
*                                                                   
* 
*                                                                                              
*    PORT  <br>   
*/
#ifndef LUCES_ICE
#define LUCES_ICE

/** \namespace RoboCompLuces
  *@brief Name space Luces
  */
module RoboCompLuces
{
  /** \interface Luces
  *@brief interface Luces
  */ 	
  interface Luces
  {
		void encender();
		void apagar();
  };
};

#endif
