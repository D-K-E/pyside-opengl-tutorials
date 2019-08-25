uniform mediump vec3 objectColor;
uniform mediump vec3 lightColor;


void main(void)
{
    gl_FragColor = vec4(objectColor * lightColor, 1.0);
}
